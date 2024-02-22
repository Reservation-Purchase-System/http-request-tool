import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests


def create_reservation_product(user_id, name, content, price, stock,
    is_reserved, open_at):
  api_endpoint = "http://localhost:8084/api/v1/products"

  # 요청 헤더에 필요한 데이터
  headers = {
    "X-USER-ID": str(user_id)
  }

  # 상품 생성 요청 데이터
  request_body = {
    "name": name,
    "content": content,
    "price": price,
    "stock": stock,
    "isReserved": is_reserved,
    "openAt": open_at
  }

  # 상품 생성 API 호출
  response = requests.post(api_endpoint, headers=headers, json=request_body)

  # 응답 확인
  if response.status_code == 201:
    print("상품 생성 성공")
    print("생성된 상품 ID:", response.headers["Location"])  # 생성된 상품 ID 확인
    return int(response.headers["Location"].split('/')[-1])
  else:
    print("상품 생성 실패:", response.json())


def scenario(user_id, product_id):
  with requests.Session() as session:
    session.keep_alive = False  # 세션에서 keep-alive 옵션 비활성화

    # 예약 상품 남은 수량 조회
    url = f"http://localhost:8087/api/v1/stocks/{product_id}"
    response = session.get(url)
    print(f"User {user_id}: findStock - {response.json()}")

  # 결제 화면 진입
  # 요청 헤더에 필요한 데이터
  url = "http://localhost:8086/api/v1/purchases"
  headers = {
    "X-USER-ID": str(user_id)
  }

  try:
    # 주문 생성 요청 데이터
    request_body = {
      "productId": product_id,  # 상품 ID를 사용하도록 수정
      "quantity": 1,
      "address": "주소"
    }

    # 주문 생성 API 호출
    with requests.post(url, headers=headers, json=request_body) as response:
      print(f"User {user_id}: 주문 ID - ",
            int(response.headers["Location"].split('/')[-1]))
      response_url = response.headers["Location"]
      purchase_id = int(response_url.split("/")[-1])

      # 20% 확률로 주문 취소
      random_num = random.randint(0, 99)
      if random_num < 20:
        cancel_url = f"http://localhost:8086/api/v1/purchases/{purchase_id}"  # 주문 ID를 사용하도록 수정
        try:
          with requests.delete(cancel_url):
            print(f"User {user_id}: 주문 취소 완료 - ", purchase_id)
            return  # 주문 취소 시에는 함수 종료

        except Exception as ex:
          print(f"User {user_id}: 주문 취소 Error : {response.json()}")
          return # 함수 종료

    # 주문이 취소되지 않은 경우에만 결제 요청 API 실행
    payment_url = "http://localhost:8085/api/v1/payments"
    payment_request_body = {
      "purchaseId": purchase_id
    }
    with requests.post(payment_url, headers=headers,
                       json=payment_request_body) as payment_response:
      if payment_response.status_code == 200:
        print(f"User {user_id}: 결제 성공!", payment_response)
      else:
        print(f"User {user_id}: 결제 실패 - ", payment_response)

  except Exception as ex:
    print(f"User {user_id}: 결제 화면 진입(주문) Error : {response.json()}")


def main():
  # 예약 상품 생성
  user_id = 1
  name = "상품 이름"
  content = "상품 설명"
  price = random.randint(1000, 10000)
  stock = 10
  is_reserved = True
  open_at = (
        datetime.now() + timedelta(days=random.randint(-30, 2))).isoformat()

  product_id = create_reservation_product(user_id, name, content, price, stock,
                                          is_reserved, open_at)

  # 결제 시나리오 요청
  num_requests = 10000

  with ThreadPoolExecutor(max_workers=1000) as executor:
    tasks = [executor.submit(scenario, user_id, product_id) for user_id in
             range(1, num_requests + 1)]

    for future in tasks:
      future.result()


if __name__ == "__main__":
  main()
