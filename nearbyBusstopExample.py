from fastapi import FastAPI
import requests

apiurl = "https://api.vworld.kr/req/search?"
params = { #장소검색 기준, 도로명 주소, 지번주소 등 설정가능
    "service": "search",
    "request": "search",
    "crs": "EPSG:4326",
    "query": "경기대 수원캠", #목적지 설정
    "type": "place",
    "format": "json",
    "key": "인증키", #인증키 부분 지우고 V-world(디지털트윈국토)에서 발급받은 api 인증키 입력
}
response = requests.get(apiurl, params=params)
adressData = None
if response.status_code == 200:
    adressData = response.json()
    print(response.json())

    destinationPointLong = adressData.get("response").get("result").get("items")[0].get("point").get("x") #중간에 배열 0은 첫번째 결과값을 꺼낸 것이므로 나중에 선택가능하면 좋을 듯
    destinationPointLati = adressData.get("response").get("result").get("items")[0].get("point").get("y") #중간에 배열 0은 첫번째 결과값을 꺼낸 것이므로 나중에 선택가능하면 좋을 듯

# API URL 및 파라미터 설정
url = "http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCrdntPrxmtSttnList"
params = {
    "serviceKey": "인증키", #인증키 부분을 지우고 공공데이터 포털 api 인증키(decode) 입력
    "gpsLati" : destinationPointLati,
    "gpsLong" : destinationPointLong,
    "numOfRows" : "10",
    "pageNo" : "1",
    "_type" : "json"
}

# GET 요청
response = requests.get(url, params=params)
busstopDataJson = response.json()
busstopData = busstopDataJson.get("response").get("body").get("items").get("item")[0].get("nodenm") #배열 0~5까지있는데 가장 가까운건 0으로 추정, 괄호로 가능하지만 문제가 생길 수 있다고 해서 get함수 사용

# 응답 출력
print(busstopData)