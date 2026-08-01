from typing import TypedDict
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pathlib import Path

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import torch


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

                #updated 
                if not docoment_loder:
                    print(f"no page is found on the - > {path},Falling back to OCR")
                    self.pdf_status.append({
                        "path":path,
                        "is_digital":False
                    })
                else:
                #per page chack instead of one Global word count.

                    digital_pgaes = sum(
                        1 for d in docoment_loder if len(d.page_content.split()) >20
                    )
                    digital_ratio = digital_pgaes / len(docoment_loder)

                    is_digital = digital_ratio>=0.6

                    if is_digital:
                        print(f"{path} is Digital pdf")
                        self.pdf_status.append({
                            "path": path,
                            "is_digital": True
                        })
                    else:
                        print(f"{path} needs OCR")
                        self.pdf_status.append({
                            "path": path,
                            "is_digital": False
                        })


            except Exception as e:
                print(e)
        return self.pdf_status


    def digital_pdf(self):
        all_docoments =[]

        for pdf in self.pdf_status:
            if pdf["is_digital"] == True:
                #the pdf is digital
                pdf_loder = PyMuPDFLoader(pdf["path"])
                docoments = pdf_loder.load()
                all_docoments.extend(docoments)

            else:
                print("use ocr techniques")

                images = convert_from_path(pdf["path"])

                for page_no, image in enumerate(images):
                    text = pytesseract.image_to_string(image)

                    all_docoments.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": pdf["path"],
                                "page": page_no + 1
                            }
                        )
                    )


        if not all_docoments:
            print("no docoment is loaded nothing to embed")
            return None

        #spliter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=200,
            chunk_overlap=40
        )

        chunk = splitter.split_documents(all_docoments)
        #device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        #embedding model
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={
                "device": device
            }
        )

        print(f"Total documents: {len(all_docoments)}")
        print(f"Total chunks: {len(chunk)}")
        print(f"Embedding device: {device}")

        #vactor store 
        #store the docoment into the vactor store
        vactor_Store = Chroma(
            collection_name="Pdf_and_imp_file_collection",
            embedding_function= embedding_model,
            persist_directory="./chromadb"
        )

        vactor_Store.add_documents(chunk)

        print("the docoment is uplodad inside the the vatore store")
        return vactor_Store



        
