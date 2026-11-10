---
title: Railway 는 진입점이 한 단계 안쪽에 있으면 서버를 못 띄운다
date: 2026-10-01
---

잘 되던 백엔드 배포가 어느 날 `railpack prepare exited with an error` 로 실패했다. 코드 문제가 아니라 시작 명령을 못 찾은 것이었다.

- Railway(Railpack)는 `main.py`, `app.py` 같은 **정해진 위치의 파일**을 보고 서버 시작 명령을 알아서 추측한다
- 옛 진입점 파일을 지우고 `app/main.py` 처럼 폴더 안쪽으로 옮기자 추측할 파일이 없어져서 실패했다
- 다음엔 처음부터 Settings 의 Custom Start Command 에 직접 적어 둔다: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (`$PORT` 는 Railway 가 정해 주는 포트라 꼭 써야 한다)
