---
title: 깃허브 프로필 README는 아이디와 같은 이름의 레포에서 나온다
date: 2026-11-10
---

깃허브 아이디와 **똑같은 이름의 공개 레포**(`dubu-alt/dubu-alt`)를 만들면, 그 레포의 `README.md`가 프로필 맨 위에 그대로 보인다.

- 레포가 Public 이어야 한다
- README 안에서 HTML 태그(`<div align="center">`, `<img>`, `<picture>`)도 대부분 쓸 수 있다
- `<picture>` + `prefers-color-scheme` 로 다크 모드 / 라이트 모드 이미지를 따로 보여줄 수 있다
