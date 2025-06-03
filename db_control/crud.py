# uname() error回避
import platform
print("platform", platform.uname())

import sqlalchemy
from sqlalchemy import create_engine, insert, delete, update, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import json
import pandas as pd

from db_control.connect_MySQL import engine
from db_control.mymodels_MySQL import Words, Progress


def myselect(Word, Progress, category, level):
    #session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(Word, Progress).outerjoin(Progress, (Word.id == Progress.word_id)).filter(Word.category == category, Word.level == level)
    try:
        #トランザクションを開始
        with session.begin():
            result = query.order_by(func.random()).limit(3).all()
        #結果をオブジェクトから辞書に変換し、リストに追加
        result_dict_list = []
        for word_info, progress in result:
            result_dict_list.append({
                "id": word_info.id,
                "text_en": word_info.text_en,
                "text_ja": word_info.text_ja,
                "translation": word_info.translation,
                "example": word_info.example,
                "is_completed": progress.is_completed if progress else False
            })
        #リストをJSONに変換
        result_json = json.dumps(result_dict_list, ensure_ascii=False)
        return result_json
    except sqlalchemy.exc.IntegrityError:
         print("一意制約違反により、挿入に失敗しました")


def myselectAll(mymodel):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = select(mymodel)
    try:
        # トランザクションを開始
        with session.begin():
            df = pd.read_sql_query(query, con=engine)
            result_json = df.to_json(orient='records', force_ascii=False)

    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        result_json = None

    # セッションを閉じる
    session.close()
    return result_json


def myinsert(mymodel, values):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()

    query = insert(mymodel).values(values).returning(*mymodel.__table__.c)
    try:
        # トランザクションを開始
        with session.begin():
            # データの挿入
            result = session.execute(query)
            inserted_row = result.fetchone()  # 複数カラムになるので fetchone()
            inserted_data = dict(inserted_row._mapping)  # Rowオブジェクトを辞書に変換
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
        inserted_data = None

    # セッションを閉じる
    session.close()
    return inserted_data


def onewordselect(mymodel, id):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(mymodel).filter(mymodel.id == id)
    try:
        # トランザクションを開始
        with session.begin():
            result = query.all()
        # 結果をオブジェクトから辞書に変換し、リストに追加
        result_dict_list = []
        for word_info in result:
            result_dict_list.append({
                "id": word_info.id,
                "text_en": word_info.text_en,
                "text_ja": word_info.text_ja,
                "translation": word_info.translation,
                "example": word_info.example,
                "category": word_info.category,
                "level": word_info.level
            })
        # リストをJSONに変換
        result_json = json.dumps(result_dict_list, ensure_ascii=False)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")

    # セッションを閉じる
    session.close()
    return result_json


def update_completion_status(mymodel, word_id, is_completed):
    # セッション作成
    Session = sessionmaker(bind=engine)
    session = Session()

    # 更新する値
    values = {
        "is_completed": is_completed,
        "completed_date": datetime.utcnow()
    }

    # UPDATE クエリ構築
    query = update(mymodel).values(values).where(Progress.word_id == word_id)

    try:
        # トランザクションを開始
        with session.begin():
            result = session.execute(query)
    except IntegrityError:
        print("一意制約違反などにより更新に失敗しました")
        session.rollback()
    finally:
        # セッションをクローズ
        session.close()

    return "put"