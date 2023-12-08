import dotenv

dotenv.load_dotenv()

import openai
import functools
from dataclasses import dataclass

client = openai.OpenAI()


def chat_complete(*, system, text):
    print("chat_complete", system, text)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content


llm = functools.partial(
    chat_complete,
    system="You are an SEO optimizer for merchant product feeds. The user will pass you their product information and you should return simply the optimized title.",
)

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///db.sqlite3", echo=True)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inputs: Mapped[str]
    title: Mapped[Optional[str]]

    def __repr__(self):
        return f"<Product(id={self.id}, inputs={self.inputs}, title={self.title})>"


Base.metadata.create_all(engine)

import streamlit as st
import pandas as pd

st.title("Product Optimizer")


@dataclass
class FeedUploadState:
    uploaded_file: pd.DataFrame = None

    @property
    def ready(self):
        return self.uploaded_file is not None


def feed_upload():
    uploaded_file = st.file_uploader("Upload your product feed")
    if uploaded_file is not None:
        # Can be used wherever a "file-like" object is accepted:
        dataframe = pd.read_csv(uploaded_file)
        st.write(dataframe)
        return FeedUploadState(uploaded_file=dataframe)
    return FeedUploadState()


def feed_optimizer(upload_state: FeedUploadState):
    if not upload_state.ready:
        return
    clicked = st.button("Optimize")
    if clicked:
        st.write("Optimizing")
        st.write("Optimized Feed")
        df = pd.DataFrame()

        def optimize_title(row):
            inputs = str(row)
            response = llm(text=inputs)
            with Session(engine) as session:
                product = Product(inputs=inputs, title=response)
                session.add(product)
                session.commit()
            return response

        df["optimized_title"] = upload_state.uploaded_file.apply(
            lambda row: optimize_title(row), axis=1
        )
        st.write(df)


upload_state = feed_upload()
feed_optimizer(upload_state)
with Session(engine) as session:
    products = session.query(Product).all()
    st.write(products)
