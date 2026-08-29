from fastapi import FastAPI
import pymysql
import os
import time

app = FastAPI()


def get_connection():
    return pymysql.connect(
        host=os.getenv("HOST_DB"),
        user=os.getenv("USER_DB"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )


@app.get("/")
def root():
    return {"message": "FastAPI is running"}


@app.get("/health")
def health():
    for _ in range(10):
        try:
            connection = get_connection()
            connection.close()
            return {"status": "ok"}
        except Exception:
            time.sleep(2)

    return {"status": "error"}


@app.get("/items")
def get_items():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, created_at FROM items ORDER BY id"
            )
            items = cursor.fetchall()

        return items
    finally:
        connection.close()


@app.post("/items/{name}")
def add_item(name: str):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO items (name) VALUES (%s)",
                (name,)
            )

        connection.commit()

        return {
            "message": "Item added",
            "name": name
        }
    finally:
        connection.close()


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM items WHERE id = %s",
                (item_id,)
            )

        connection.commit()

        return {
            "message": "Item deleted",
            "id": item_id
        }
    finally:
        connection.close()