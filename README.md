# DART 공시파일 HTML로 저장/입수 Data의 1차 가공
## 개요
FSS는 오픈API(https://opendart.fss.or.kr/intro/main.do) 에서 Macro Data를 제공하고 있다. 여기서 제시하는 여러 코드는 FSS 제공 Data의 범위(종류, 기간)를 벗어난 정보가 필요할 때 사용한다.
예를 들면 외부감사실시내역 상 감사시간이나 사업보고서 감사에 관한 사항에 제시되는 감사보수 정보가 그렇다. 

## 코드 종류
### Disclosure-to-HTML
#### 코드: scraper
DART 공시파일 중, 예를 들면, 사업보고서는 다음과 같은 문서 계층 구조를 사용하고 있다.
