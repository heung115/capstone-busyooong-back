# -*- coding: utf-8 -*-
from fastapi import FastAPI
import requests
import urllib.parse
from env import getEnv
from supabase import create_client, Client
import math

distanceStandard = 1
newResultBusStop = None

COORDINATE_URL = "http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCrdntPrxmtSttnList"
COORDINATE_PARAMS = {
    # 인증키 부분을 지우고 공공데이터 포털 api 인증키(decode) 입력
    "serviceKey": getEnv("DATA_GO_KEY"),
    "gpsLati": None,
    "gpsLong": None,
    "numOfRows": "10",
    "pageNo": "1",
    "_type": "json"
}


def coordinateRequest(pointLati, pointLong):
    """
    위도, 경도를 기반으로 하는 버스 정류장 찾기를 위한 API 요청 함수

    :param pointLati: 목표 경도 - float
    :param pointLong: 목표 위도 - float
    :return: API 요청 결과 - json
    """
    global COORDINATE_URL
    global COORDINATE_PARAMS

    # 기존의 params 딕셔너리를 쿼리 문자열로 변환
    queryParams = urllib.parse.urlencode(COORDINATE_PARAMS)
    # 변환된 쿼리 문자열을 딕셔너리로 다시 파싱
    parsedParams = dict(urllib.parse.parse_qsl(queryParams))

    # gpsLati 값을 받아온 위치 값으로 수정
    parsedParams["gpsLati"] = pointLati
    parsedParams["gpsLong"] = pointLong

    # 새로운 쿼리 문자열을 생성
    modifiedParam = urllib.parse.urlencode(parsedParams)

    # api 요청
    response = requests.get(COORDINATE_URL, params=modifiedParam)

    busStopBodyJson = response.json().get("response").get("body")

    return busStopBodyJson


def coordinateCheckResult(requestResult, successCount, pointLati, pointLong):
    """
    위도, 경도 기반 request에 대한 결과를 확인 함수

    :param requestResult: request 결과
    :param successCount: 현재 Count
    :return: list - [새로운 버스 정류장 정보, successCount + 1]
    """
    global distanceStandard
    global newResultBusStop

    if requestResult.get("totalCount") == 1:
        successCount += 1
        print("버스정류소 검색 body데이터 :", requestResult['items']['item'])
        busLati = requestResult.get("items").get("item").get("gpslati")
        busLong = requestResult.get("items").get("item").get("gpslong")
        latiDistanceDiffelence = float(pointLati) - float(busLati)
        longDistanceDiffelence = float(pointLong) - float(busLong)
        distance = math.sqrt(math.pow(latiDistanceDiffelence, 2) + math.pow(longDistanceDiffelence, 2))
        # 가장 가까운 노선일 경우에만 버스정류장 정보 저장
        if distanceStandard > distance:
            print("수정완료")
            distanceStandard = distance
            # 버스정류장 정보
            # newResultBusStop = requestResult.get("items").get("item").get("nodenm")
            newResultBusStop = [requestResult.get("items").get("item").get("nodenm"),
                                requestResult.get("items").get("item").get("nodeid"),
                                requestResult.get("items").get("item").get("citycode")]

    elif requestResult.get("totalCount") != 0:
        # 검색결과가 여러개이면
        successCount += 1
        print("버스정류소 검색 body데이터 :", requestResult['items']['item'][0])
        busLati = requestResult.get("items").get("item")[0].get("gpslati")
        busLong = requestResult.get("items").get("item")[0].get("gpslong")
        latiDistanceDiffelence = float(pointLati) - float(busLati)
        longDistanceDiffelence = float(pointLong) - float(busLong)
        distance = math.sqrt(math.pow(latiDistanceDiffelence, 2) + math.pow(longDistanceDiffelence, 2))
        # 가장 가까운 노선일 경우에만 버스정류장 정보 저장
        if distanceStandard > distance:
            print("수정완료")
            distanceStandard = distance
            # 가장 가까운 0번 선택
            # newResultBusStop = requestResult.get("items").get("item")[0].get("nodenm")
            newResultBusStop = [requestResult.get("items").get("item")[0].get("nodenm"),
                                requestResult.get("items").get("item")[0].get("nodeid"),
                                requestResult.get("items").get("item")[0].get("citycode")]
    else:
        print("버스정류소 검색 body데이터 : 없음")

    return [newResultBusStop, successCount]


def coordinateBusStopSearch(pointLati, pointLong):
    """
    좌표를 이용하여 근처의 버스정류소를 검색

    :param pointLati: 위도 데이터 - float
    :param pointLong: 경도 데이터 - float
    :return: 버스 정류장 데이터 - list : [bus stop name, bus stop id]
    """

    busstopBodyJson = coordinateRequest(pointLati, pointLong)

    resultBusStop = None
    global distanceStandard
    # 검색결과가 없으면 범위를 500m씩 넓혀서 검색하는 알고리즘 실행 같이 보낸 링크참고
    if busstopBodyJson.get("totalCount") == 0:
        successCount = 0
        # 반복 횟수
        numberOfImplementation = 1

        # 검색결과가 하나이상 나올경우 한바퀴 돌고나서 중단함 없으면 범위를 넓혀 반복
        while successCount == 0:
            # 500m당 위/경도 서울 기준 약 0.0045도
            firstCoordinateLati = pointLati - numberOfImplementation * 0.0045
            firstCoordinateLong = pointLong - numberOfImplementation * 0.0045

            nowLat = pointLati - numberOfImplementation * 0.0045
            nowLong = pointLong - numberOfImplementation * 0.0045

            # make gabLoc
            maxGab = numberOfImplementation * 0.0045 * 2
            gabList = [(0, 0), (maxGab, 0), (0, maxGab), (maxGab, maxGab)]
            for i in range(1, numberOfImplementation * 2):
                nowGab = i * 0.0045
                gabList.append((0, nowGab))
                gabList.append((maxGab, nowGab))
                gabList.append((nowGab, 0))
                gabList.append((nowGab, maxGab))

            busstopBodyJson = coordinateRequest(firstCoordinateLati, firstCoordinateLong)
            resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount, pointLati, pointLong)

            for latGab, longGab in gabList:
                nowLat, nowLong = firstCoordinateLati - latGab, firstCoordinateLong - longGab

                busstopBodyJson = coordinateRequest(nowLat, nowLong)

                resultBusStop, successCount = coordinateCheckResult(busstopBodyJson, successCount, pointLati, pointLong)
                if resultBusStop is not None and getAllPathId(*resultBusStop):
                    break

            numberOfImplementation += 1
    else:
        resultBusStop = coordinateCheckResult(busstopBodyJson, 0, pointLati, pointLong)[0]

    distanceStandard = 1
    return resultBusStop  # 지금은 마지막에 검색된 곳을 리턴해줌
    # TODO pointLati와 버스정류장 거리를 피타고라스로 계산 후 가장 가까운 곳 추천


def getDestinationLoc(destination):
    """
    목적지명 기준으로 목저지의 위도, 경도을 알아냄. (이해한게 맞다면)

    :param destination: 목적지명 - string
    :return: 목적지 위도, 경도 - list(위도, 경도)
    """
    apiurl = "https://api.vworld.kr/req/search?"
    params = {
        # 장소검색 기준
        "service": "search",
        "request": "search",
        "crs": "EPSG:4326",
        # 목적지 설정 - destination으로 대체 되는 것 같음.
        "query": destination,
        "type": "place",
        "format": "json",
        # 인증키 부분 지우고 V-world(디지털트윈국토)에서 발급받은 api 인증키 입력
        "key": getEnv("V_WORLD_KEY"),
    }
    response = requests.get(apiurl, params=params)
    res = [-1, -1]
    if response.status_code == 200:
        adressData = response.json()
        # print("장소검색 데이터 :", response.json())

        # 결과 값의 x,y좌표 꺼내기
        # 중간에 배열 0은 첫번째 결과값을 꺼낸 것이므로 나중에 소비자가 선택가능하면 좋을 듯
        res[1] = float(adressData.get("response").get("result").get("items")[0].get("point").get("x"))
        res[0] = float(adressData.get("response").get("result").get("items")[0].get("point").get("y"))
    return res


def getAllPathId(busStopName, busStopId, cityCode):
    """
    출발 버스 정류장을 지나는 모든 버스 노선 id를 반환 - 불필요할 할지도

    :param busStopName: 출발 버스 정류장 이름
    :param busStopId: 출발 버스 정류장 id
    :param cityCode: 출발 버스 정류장 아이디
    :return: list [노선 ID...]
    """
    busPathURL = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getSttnThrghRouteList'

    params = {
        "serviceKey": getEnv("DATA_GO_KEY"),
        "_type": "json",
        "numOfRows": "10",
        "pageNo": "1",
        "cityCode": cityCode,
        "nodeid": busStopId
    }

    response = requests.get(busPathURL, params=params)

    pathJson = response.json().get("response").get("body")

    if pathJson['totalCount'] == 1:
        return [pathJson['items']['item']['routeid']]
    elif pathJson['totalCount'] > 1:
        routeIds = []
        for item in pathJson['items']['item']:
            routeIds.append(item['routeid'])
        return routeIds

    return []


def getAllViaBusStop(busRouteId, cityCode):
    url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '10', '_type': 'json',
              'cityCode': cityCode,
              'routeId': busRouteId}

    response = requests.get(url, params=params).json()['response']['body']['items']['item']

    return response


def busArrivalTime(pathId, busStopId, cityCode):
    url = 'http://apis.data.go.kr/1613000/ArvlInfoInqireService/getSttnAcctoSpcifyRouteBusArvlPrearngeInfoList'
    params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '10', '_type': 'json',
              'cityCode': cityCode, 'nodeId': busStopId, 'routeId': ''}
    busTimeDic = {}

    for routeId in pathId:
        # 찾은 노선 리스트에서 노선Id를 받아와 도착시간을 구하고 Id와 시간을 딕셔너리에 저장
        params["routeId"] = routeId
        print(params["routeId"])
        response = requests.get(url, params=params).json()
        busTimeDic[routeId] = int(response["response"]["body"]["items"]["item"][0]["arrtime"])
        print(busTimeDic)
    # 도착 순서대로 정렬하여 리스트에 담아 리턴
    sortedBus = list(dict(sorted(busTimeDic.items(), key=lambda x: x[1])).keys())
    return sortedBus


def shortestBusRoute(pathId, userStartId, userEndId, cityCode):
    url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '10', '_type': 'json',
              'cityCode': cityCode, 'routeId': ''}
    shortPathDic = {}
    sortedBus = []
    for routeId in pathId:
        startOrd, endOrd = 0, 0
        params["routeId"] = routeId
        response = requests.get(url, params=params).json()
        pathList = response["response"]["items"]["item"]
        # 출발 정류장과 도착 정류장 사이 정류장 개수를 구하여 딕셔너리에 저장
        for routeList in pathList:
            if routeList["nodeid"].count(userStartId) == 1:
                startOrd = int(routeList["nodeord"])
            if routeList["nodeid"].count(userEndId) == 1:
                endOrd = int(routeList["nodeord"])
        shortPathDic[routeId] = abs(startOrd - endOrd)
    # 사이에 정류장이 적은 순으로 정렬 후 리스트에 담아 리턴
    sortedBus = list(dict(sorted(shortPathDic.items(), key=lambda x: x[1])).keys())
    return sortedBus


def findBus(userLati, userLong, userDestination):
    # [busStopName, busStopID, cityCode]
    userStart = coordinateBusStopSearch(userLati, userLong)
    print(userStart)

    destinationPointLati, destinationPointLong = getDestinationLoc(userDestination)
    userEnd = coordinateBusStopSearch(destinationPointLati, destinationPointLong)
    print(userEnd)

    userStartAllPathId = getAllPathId(*userStart)
    userEndAllPathId = getAllPathId(*userEnd)

    crossPathIds = set()
    for pathId in userStartAllPathId:
        viaBusStops = getAllViaBusStop(pathId, userStart[-1])

        for busStop in viaBusStops:
            if busStop['nodenm'].find(userEnd[0]) != -1:
                crossPathIds.add(pathId)
    for pathId in userEndAllPathId:
        viaBusStops = getAllViaBusStop(pathId, userEnd[-1])

        for busStop in viaBusStops:
            if busStop['nodenm'].find(userStart[0]) != -1:
                crossPathIds.add(pathId)

    print(crossPathIds)


    res1 = busArrivalTime(crossPathIds, userStart[1], userStart[-1])
    res2 = shortestBusRoute(crossPathIds, userStart[1], userEnd[1], userStart[-1])

    if len(res1) == 0 and len(res2) == 0:
        return {
            "status": False
        }

    return {
        "status": True,
        "city_code": userStart[-1],
        "fast_arrive": res1,
        "short_time": res2,
        "start_bus_stop": [userStart[0], userStart[1]]
    }


if __name__ == "__main__":
    # test cod
    findBus(37.41909998804243, 126.93540006310809, "경기대 수원캠")
    pass

    # === supabase test start ===
    # url: str = getEnv("SUPABASE_URL")
    # key: str = getEnv("SUPABASE_KEY")
    # supabase: Client = create_client(url, key)

    # supabase.table("nodes").select("NODE_NM").execute()
    # supabase.table(("bus_stop_name")).insert(json={
    #     "bus_stop_name": "test",
    #     "gps_lati": 0.1010,
    #     "gps_long": 4.123,
    #     "bus_stop_id": "test"
    # }).execute()
    # === supabse test end ===

    # === 출발지 목적지 모든 버스 경로 테스트 ===
    # userLati, userLong = getDestinationLoc("의왕톨 게이트")
    # print("user loc :", userLati, userLong)
    userLati, userLong = 37.34849196408942, 126.98445190777875
    # busStopData = coordinateBusStopSearch(userLati, userLong)
    # busStopData = ['의왕톨게이트', 'GGB226000038', 31170]
    # print("bus_stop_data :", busStopData)
    #
    # userStartAllPathId = getAllPathId(*busStopData)
    #
    # print("bus_route_ids :", userStartAllPathId)
    #
    # crossPathIds = []
    # destinationName = "장안"
    # for pathId in userStartAllPathId:
    #     viaBusStops = getAllViaBusStop(pathId, busStopData[-1])
    #
    #     for busStop in viaBusStops:
    #         if busStop['nodenm'].find(destinationName) != -1:
    #             crossPathIds.append(pathId)
    #
    # print(crossPathIds)

    # 사용자위치는 임의설정(반경 500m내 버스정류장 없는 곳으로 하였음) 프론트에서 나중에 받을 예정
    # userPointLong = 126.972781
    # userPointLati = 37.555459
    # # 37.535897, 127.005406
    # busstopData = coordinateBusStopSearch(userPointLati, userPointLong)
    # # # lati, long = getDestinationLoc("서울역")
    # # # print(lati, long)
    # # # busstopData = coordinateBusStopSearch(lati, long)
    # print(busstopData)
    # print("===========")

    # === 모든 city code 조회 test ===
    # url = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCtyCodeList'
    # params = {'serviceKey': getEnv("DATA_GO_KEY"), '_type': 'json'}
    # response = requests.get(url, params=params)
    # print(response.json())
    # === test end ===

    # print("============")
    # for data in response.json()['response']['body']['items']['item']:
    #     cityCode = data['citycode']
    #     cityname = data['cityname']
    #
    #     print(f'{cityCode} start')
    #
    #     url = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getSttnNoList'
    #     params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '6637', '_type': 'json',
    #               'cityCode': f'{cityCode}',
    #               }
    #     res = requests.get(url, params=params).json()
    #
    #     if res["response"]['body']['totalCount'] == 0:
    #         continue
    #
    #     totalCount = res["response"]['body']['totalCount']
    #     params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': f'{totalCount}', '_type': 'json',
    #               'cityCode': f'{cityCode}',
    #               }
    #     res = requests.get(url, params=params).json()
    #     data = []
    #
    #     for d in res['response']['body']['items']['item']:
    #         d.pop('nodeno', None)
    #         d['citycode'] = cityCode
    #         data.append(d)
    #     supabase.table("bus_stop_name").insert(data).execute()
    #
    #
    #
    #     print(f'{cityCode} end')
    # url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteNoList'
    # params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '10', '_type': 'json', 'cityCode': '31010', 'routeNo': '8800'}
    #
    # response = requests.get(url, params=params)
    # print(response.json())
    # print("==============")
    #
    # url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    # params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '65', '_type': 'json', 'cityCode': '31010',
    #           'routeId': 'GGB200000205'}
    #
    # response = requests.get(url, params=params)
    # print(response.json())
    #
    # url = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getSttnNoList'
    # params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '6637', '_type': 'json', 'cityCode': '31030',
    #           }# 'nodeNm': '서울역버스환승센터(6번승강장)(중)'}
    # response = requests.get(url, params=params)
    # print("===============")
    # print(response.json())
    # startAllpath = getAllPath(*busstopData)
    # print(busstopData)
    # print(startAllpath)
    #
    # for s in startAllpath:
    #     # url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    #     url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteInfoIem'
    #     # params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '100', '_type': 'json', 'cityCode': busstopData[2],
    #     #      'routeId': s}
    #     params = {'serviceKey': getEnv("DATA_GO_KEY"), '_type': 'json', 'cityCode': busstopData[2], 'routeId': s}
    #     response = requests.get(url, params=params)
    #     print(response.json()['response']['body']['items']['item']['routeno'])

    #
    # # 응답 출력
    # # print("출발지 버스정류소 :", busstopData)
    # destinationPointLati, destinationPointLong = getDestinationLoc("경기대후문.수원박물관")
    # busstopData = coordinateBusStopSearch(destinationPointLati, destinationPointLong)
    # endAllpath = getAllPath(*busstopData)
    # print(busstopData)
    # print(endAllpath)
    #
    # for s in endAllpath:
    #     # url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    #     url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteInfoIem'
    #     # params = {'serviceKey': getEnv("DATA_GO_KEY"), 'pageNo': '1', 'numOfRows': '100', '_type': 'json', 'cityCode': busstopData[2],
    #     #      'routeId': s}
    #     params = {'serviceKey': getEnv("DATA_GO_KEY"), '_type': 'json', 'cityCode': busstopData[2], 'routeId': s}
    #     response = requests.get(url, params=params)
    #     print(response.json()['response']['body']['items']['item']['routeno'])

    # print(busstopData)
    # # 응답 출력
    # print("목적지 버스정류소 :", busstopData)
