from typing import TypedDict
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pathlib import Path

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from langchain_core.documents import Document



class DocumentAnalysis(TypedDict):
    file_path:str
    dociment_text: str
    clauses :list
    risk :list
    missing_clauses :list 
    summery :str


class UploadFile:
    def __init__(self, paths: list[str],pdf_status:list | None = None):
        self.paths = paths
        self.pdf_status = pdf_status or []

    def scan_pdfs(self):



        for path in self.paths:
            try : 
                loder = PyMuPDFLoader(path)
                docoment_loder =loder.load()

                total_text = "".join(
                    doc.page_content.strip()
                    for doc in docoment_loder
                )

            
                word_count =  bool(total_text.strip())
                if word_count > 100:
                    print("Digital page pdf")
                    
                    self.pdf_status.append({
                        "path":path,
                        "is_digital":True
                    })
                else:
                    print("use ocr techniqu")

                    self.pdf_status.append({
                        "path":path,
                        "is_digital":False
                    })
            except Exception as e:
                print(e)
        return self.pdf_status


    def digital_pdf(self):
        all_docoments =[]

        for pdf in self.pdf_statuss:
            if pdf["is_digital"] == True:
                #the pdf is digital
                pdf_loder = PyMuPDFLoader(pdf["path"])
                docoments = pdf_loder.load()
                all_docoments.extend(docoments)

            else:
                print("use ocr techniques")
                images = convert_from_path(pdf["path"])
                text = ""
                for image in images:
                    text += pytesseract.image_to_string(image,lang="eng")

                all_docoments.append(
                    Document(
                        page_content=text,
                        metadata = {"source":pdf["path"]}
                    )
                )

        return all_docoments


        
