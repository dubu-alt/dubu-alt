---
title: sqlite3.connect 는 DB 파일이 없으면 에러 대신 빈 DB 를 새로 만든다
date: 2026-11-10
---

서버는 멀쩡히 돌아가는데 DB 확인 명령만 `no such table: posts` 에러를 냈다.

- `sqlite3.connect('database.db')`는 **상대경로**라서 터미널이 지금 있는 폴더를 기준으로 파일을 찾는다
- 파일이 없으면 에러를 내지 않고 **빈 DB 파일을 새로 만든다**. 그래서 테이블이 없다는 엉뚱한 에러가 나고, 쓸모없는 빈 파일까지 남는다
- 읽기 전용으로 열면 새 파일을 만들지 않고 바로 실패해서 원인을 알기 쉽다: `sqlite3.connect('file:database.db?mode=ro', uri=True)`
- 다음엔 `pwd`로 위치부터 확인하고, 앱 코드에서는 `Path(__file__)` 기준 **절대경로**로 DB 위치를 고정한다
