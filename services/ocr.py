"""Optional, local Windows OCR for image-only PDFs. No remote service is used."""
# Import io so this file can use its functions and classes.
import io
# Import os so this file can use its functions and classes.
import os
# Bring the listed helpers from pathlib into this file.
from pathlib import Path
# Import shutil so this file can use its functions and classes.
import shutil
# Import subprocess so this file can use its functions and classes.
import subprocess
# Import tempfile so this file can use its functions and classes.
import tempfile


# Validate a scanned PDF, then run Windows OCR or the Linux OCR adapter.
def ocr_pdf(content, work_root):
    if os.name != 'nt':
        return portable_ocr_pdf(content, work_root)
    if not content or len(content)>10*1024*1024 or not content.startswith(b'%PDF-'):
        raise ValueError('Choose a valid PDF up to 10 MB.')
    # Bring the listed helpers from pypdf into this file.
    from pypdf import PdfReader
    # Handle expected failures here so the app can show a readable error.
    try:
        reader=PdfReader(io.BytesIO(content))
        if reader.is_encrypted: raise ValueError('Encrypted PDFs are not supported.')
        if len(reader.pages)>20: raise ValueError('Scanned PDFs must contain at most 20 pages. Split the statement into smaller files.')
    # Catch this type of failure instead of continuing with invalid data.
    except ValueError:
        raise
    # Catch this type of failure instead of continuing with invalid data.
    except Exception as exc:
        raise ValueError('The PDF could not be opened for OCR.') from exc
    root=Path(work_root)/'ocr-temp';root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as temporary:
        folder=Path(temporary).resolve();source=folder/'input.pdf';target=folder/'text.txt'
        source.write_bytes(content)
        # Handle expected failures here so the app can show a readable error.
        try:
            script=Path(__file__).with_name('windows_ocr.ps1').read_text().split('\n',1)[1]
            command='$InputPath=$env:SMARTBUDGET_OCR_INPUT; $OutputPath=$env:SMARTBUDGET_OCR_OUTPUT; '+script
            environment={**os.environ,'SMARTBUDGET_OCR_INPUT':str(source),'SMARTBUDGET_OCR_OUTPUT':str(target)}
            result=subprocess.run([shutil.which('powershell.exe'),'-NoProfile','-NonInteractive','-Command',command],env=environment,capture_output=True,timeout=180,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        # Catch this type of failure instead of continuing with invalid data.
        except subprocess.TimeoutExpired as exc:
            raise ValueError('OCR took too long. Split the PDF into fewer pages and try again.') from exc
        if result.returncode or not target.exists():
            raise ValueError('Windows OCR could not read this file. Check that the English OCR language feature is installed, or try a clearer scan or a text-based PDF/CSV.')
        text=target.read_text(encoding='utf-8').strip()
        if not text: raise ValueError('OCR found no readable text. Try a clearer scan or a text-based PDF/CSV.')
        if len(text)>1_000_000: raise ValueError('OCR text exceeds the one-million-character limit.')
        return text

# Validate and rotate a receipt photo, then wrap it as a PDF for OCR.
def photo_to_pdf(content):
    """Wrap a captured receipt image as PDF for the local OCR pipeline."""
    if not content or len(content)>10*1024*1024:
        raise ValueError('Choose a receipt photo up to 10 MB.')
    # Bring the listed helpers from PIL into this file.
    from PIL import Image, ImageOps, UnidentifiedImageError
    # Handle expected failures here so the app can show a readable error.
    try:
        with Image.open(io.BytesIO(content)) as source:
            if source.format not in ('JPEG','PNG'):
                raise ValueError('Choose a JPEG or PNG receipt photo.')
            if source.width*source.height>16_000_000:
                raise ValueError('The photo is too large. Use a photo below 16 megapixels.')
            image=ImageOps.exif_transpose(source).convert('RGB')
            # Handle expected failures here so the app can show a readable error.
            try:
                output=io.BytesIO();image.save(output,format='PDF',resolution=150.0)
            finally:
                image.close()
        pdf=output.getvalue()
        if len(pdf)>10*1024*1024: raise ValueError('The converted photo exceeds 10 MB. Use a smaller photo.')
        return pdf
    # Catch this type of failure instead of continuing with invalid data.
    except (UnidentifiedImageError,OSError,Image.DecompressionBombError) as exc:
        raise ValueError('This image could not be opened. Use a clear JPEG or PNG receipt photo.') from exc


# Use Poppler to render PDF pages and Tesseract to read their text on the server.
def portable_ocr_pdf(content, work_root):
    """Read scans on Linux/Streamlit Cloud using server-local Poppler and Tesseract."""
    if not content or len(content)>10*1024*1024 or not content.startswith(b'%PDF-'):
        raise ValueError('Choose a valid PDF up to 10 MB.')
    # Bring the listed helpers from pypdf into this file.
    from pypdf import PdfReader
    # Handle expected failures here so the app can show a readable error.
    try:
        reader=PdfReader(io.BytesIO(content))
        if reader.is_encrypted: raise ValueError('Encrypted PDFs are not supported.')
        if len(reader.pages)>20: raise ValueError('Scanned PDFs must contain at most 20 pages.')
    # Catch this type of failure instead of continuing with invalid data.
    except ValueError:
        raise
    # Catch this type of failure instead of continuing with invalid data.
    except Exception as exc:
        raise ValueError('The PDF could not be opened for OCR.') from exc
    renderer=shutil.which('pdftoppm'); engine=shutil.which('tesseract')
    if not renderer or not engine:
        raise ValueError('Receipt OCR needs Poppler and Tesseract installed on this server. On Streamlit Cloud, deploy with packages.txt.')
    root=Path(work_root)/'ocr-temp'; root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root) as temporary:
        folder=Path(temporary); source=folder/'input.pdf'; source.write_bytes(content)
        # Import time so this file can use its functions and classes.
        import time
        deadline=time.monotonic()+180
        parts=[]
        # Handle expected failures here so the app can show a readable error.
        try:
            for index in range(len(reader.pages)):
                prefix=folder/'page'
                rendered=subprocess.run([renderer,'-f',str(index+1),'-l',str(index+1),'-singlefile','-scale-to','2400','-png',str(source),str(prefix)],capture_output=True,timeout=max(1,deadline-time.monotonic()))
                if rendered.returncode:
                    raise ValueError('OCR could not render this PDF. Try a clearer receipt photo.')
                read=subprocess.run([engine,str(prefix)+'.png','stdout','-l','eng'],capture_output=True,timeout=max(1,deadline-time.monotonic()))
                if read.returncode:
                    raise ValueError('OCR could not read this receipt. Try a clearer photo.')
                parts.append(read.stdout.decode('utf-8',errors='replace'))
                if sum(map(len,parts))>1_000_000:
                    raise ValueError('OCR text exceeds the one-million-character limit.')
        # Catch this type of failure instead of continuing with invalid data.
        except subprocess.TimeoutExpired as exc:
            raise ValueError('OCR took too long. Use fewer pages or a smaller image.') from exc
        text='\n'.join(parts).strip()
        if not text: raise ValueError('OCR found no readable text. Try a clearer receipt photo.')
        return text
