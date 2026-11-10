---
title: SQLAlchemy 의 add 는 SQL 을 보내지 않고 commit 때 INSERT 가 나간다
date: 2026-11-10
---

`add`, `commit` 이 실제로 어떤 SQL 이 되는지 궁금해서 SQL 로그를 켜고 확인했다.

- `db.add(obj)`는 세션에 **등록만** 한다. 실제 `INSERT`는 `commit()` 때(정확히는 commit 직전의 flush 때) 실행된다
- 수정할 때 UPDATE 문을 따로 쓰지 않는다. 속성을 바꾸고 `commit()` 하면 세션이 **바뀐 칸만** `UPDATE ... SET title=?` 으로 보낸다
- `commit()` 뒤에 `refresh(obj)`를 하면 DB가 만든 id와 기본값을 `SELECT`로 다시 읽어 온다
- 다음엔 `create_engine(url, echo=True)`로 실제 SQL을 로그로 보면서 확인한다
