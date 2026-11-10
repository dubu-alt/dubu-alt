---
title: FastAPI 게시판을 만들며 스스로 답해 본 질문들
date: 2026-11-10
---

FastAPI + SQLAlchemy + Jinja2로 공부 기록 블로그를 만들고, 동료 평가를 준비하며 받은 질문과 내 답을 한곳에 모았다.

**흐름과 레이어**

- 저장 버튼을 누르면? `POST /posts` → **라우터**(`Form()`으로 값 받기) → **서비스**(공백 제거·필수값 검증) → **저장소**(`add` → `commit`) → DB → `PostRead`로 포장 → **303 리다이렉트**
- 레이어 분리 = 요청·응답 구조? 아니다. 요청·응답은 **서버 바깥**(브라우저 ↔ 서버) 통신이고, 레이어는 **서버 안** 코드의 역할 분리다
- 라우터와 서비스를 나누는 기준은 **"HTTP를 아는가"** 다. `Form`, `RedirectResponse`, `TemplateResponse`는 라우터에만 둔다
- 라우터에 다 넣으면? 검증이 등록·수정에 **복사**되고, DB 코드가 흩어져 DB를 바꿀 때 전부 고쳐야 하고, API 전환과 테스트가 어려워진다
- SSR을 REST로 바꾸면 **라우터와 템플릿만** 바뀌고 서비스·저장소·모델·스키마는 그대로 쓴다
- 앱도 만들어야 하면 HTML이 아니라 JSON이 필요하니 **REST API** 가 유리하다

**DB와 SQLAlchemy (파이썬 ORM 라이브러리)**
- ORM (객채-관계 매핑)은 **클래스 = 테이블, 객체 = 행** 으로 이어 주는 통역사다. 즉, SQL을 직접 쓰지 않고도 파이썬 코드로 DB를 다룰수 있다.
- `db.add()`는 SQL을 안 보낸다. `commit()` 때 `INSERT`, 속성을 바꾸고 commit하면 **바뀐 칸만** `UPDATE`, `refresh()`는 `SELECT`로 다시 읽는다. `echo=True`로 확인한다
- `get_db()`가 `yield`인 이유: 요청마다 세션을 빌려주고, 응답 뒤 `finally`에서 **에러가 나도** `close()` 해서 연결을 풀에 반납한다. `return`이면 사용 후 정리할 기회가 없다
- `models`는 DB 쪽 **테이블 설계도**(저장소가 씀), `schemas`는 화면 쪽 **포장 상자(DTO)**(서비스가 씀). 화면에 숨길 칸은 models에만 두고 schemas에는 넣지 않는다
- DB를 PostgreSQL로 바꾸려면 드라이버를 설치하고 **`DATABASE_URL` 환경변수**만 바꾼다. 서비스는 저장소 함수 이름만 알아서 그대로다
- `create_all()`은 **없는 테이블만** 만든다. 기존 테이블에 칸을 추가하려면 DB를 새로 만들거나 **Alembic** 으로 마이그레이션한다
- 연관관계(카테고리 1 : 글 N)를 넣으면 `ForeignKey` + `relationship`을 추가하고, 바뀌는 곳은 주로 **모델·저장소·서비스** 다

```sql
# SQL_직접 사용시
cursor.execute("SELECT * FROM posts WHERE id = ?", (3,))
row = cursor.fetchone()
print(row[1])          # 1번 칸이 제목이었나…? 순서를 외워야 함
```

```python
# ORM(SQLAlchemy) 사용시
post = db.get(Post, 3)
print(post.title)      # 이름으로 바로 접근
```

**GET/POST와 PRG (POST,REDIRIECTION,GET)**

- GET은 **조회**(주소에 남고 새로고침 안전), POST는 **변경**. 그래서 검색은 GET, 삭제는 링크가 아니라 POST 버튼이다
- POST 뒤 화면을 바로 그리면 F5에 **POST가 재전송**돼 중복 저장된다. 그래서 리다이렉트로 마지막 요청을 GET으로 바꾼다
- `RedirectResponse` 기본값은 **307**(POST 유지)이라 **303**(GET으로 가라)을 직접 지정한다. 다시 GET을 보내는 건 사용자가 아니라 **브라우저가 자동으로** 한다
- 검증 실패 땐 리다이렉트하지 않는다. 입력값과 에러 문구를 유지한 채 폼을 **400**으로 다시 보여 준다

**Jinja2와 보안**

- Jinja2는 HTML의 템플릿의 빈칸 데이터를 채워 완성된 HTML을 만드는 템플릿 엔진이다.
- `{{ }}`는 **출력**, `{% %}`는 **명령**(if, for, extends)이다
- Jinja2는 `<`, `>`를 자동으로 **이스케이프**해서 `<script>`가 글자로만 보인다(XSS 방어). 사용자 입력에 `| safe`를 쓰면 이 방어가 꺼진다

**다음에 써먹을 포인트**

- 새 코드를 넣을 땐 "HTTP를 아는가? 규칙인가? DB인가?"로 들어갈 레이어를 먼저 정한다
