import random
from concurrent.futures import ThreadPoolExecutor

import requests


def scenario(user_id):
  with requests.Session() as session:
    session.keep_alive = False  # 세션에서 keep-alive 옵션 비활성화

    # 예약 상품 남은 수량 조회
    reservation_id = random.randint(1, 100)
    url = f"http://localhost:8083/product-service/reservation-products/{reservation_id}/stock"
    try:
      response = session.get(url)
      print(f"재고 수량 - {response.json()['stock']}")
    except Exception as ex:
      print(f"재고 조회 Error to {url}: {ex}")
      return

  # 결제 화면 진입
  # 요청 헤더에 필요한 데이터
  url = "http://localhost:8083/purchase-service/purchases"
  headers = {
    "X-USER-ID": str(user_id)
  }
  response = None

  try:
    # 주문 생성 요청 데이터
    request_body = {
      "productId": random.randint(1, 100),
      "quantity": 1,
      "productType": "reservationProduct",
      "address": "주소"
    }

    # 주문 생성 API 호출
    with requests.post(url, headers=headers, json=request_body) as response:
      print(f"주문 ID: ", response.headers["Location"])
      response_url = response.headers["Location"]
      purchase_id = int(response_url.split("/")[-1])

      # 20% 고객 주문 취소
      random_num = random.randint(0, 99)
      if random_num < 20:
        cancel_url = "http://localhost:8083/purchase-service/purchases?id=" + str(purchase_id)
        try:
          with requests.delete(cancel_url) as cancel_response:
            print(f"주문 취소 완료: ", purchase_id)
        except Exception as ex:
          print(f"주문 취소 Error to {cancel_url}: {ex}")

      # 결제 요청 API
      payment_url = "http://localhost:8083/payment-service/payments"
      try:
        payment_request_body = {
          "purchaseId": purchase_id
        }
        with requests.post(payment_url, headers=headers, json=payment_request_body) as payment_response:
          print(f"결제: ", payment_response)
      except Exception as ex:
        print(f"결제 요청 Error to {payment_url}: {ex}")

  except Exception as ex:
    print(f"결제 화면 진입(주문) Error to {url}: {ex}")


def main():
  # 결제 시나리오 요청
  num_requests = 10000

  with ThreadPoolExecutor(max_workers=1000) as executor:
    tasks = [executor.submit(scenario, user_id) for user_id in range(1, num_requests + 1)]

    for future in tasks:
      future.result()


if __name__ == "__main__":
  main()
