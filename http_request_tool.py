import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests
import time


def create_reservation_product(user_id, name, content, price, stock,
    is_reserved, open_at):
  api_endpoint = "http://localhost:8083/test/product-service/products"

  headers = {
    "X-USER-ID": str(user_id)
  }

  request_body = {
    "name": name,
    "content": content,
    "price": price,
    "stock": stock,
    "isReserved": is_reserved,
    "openAt": open_at
  }

  response = requests.post(api_endpoint, headers=headers, json=request_body)

  if response.status_code == 201:
    print("상품 생성 성공")
    print("생성된 상품 ID:", response.headers["Location"])
    return int(response.headers["Location"].split('/')[-1])
  else:
    print("상품 생성 실패:", response.json())


def scenario(user_id, product_id):
  # 남은 재고 조회
  url = f"http://localhost:8083/test/stock-service/stocks/{product_id}"

  try:
    response = requests.get(url, verify=False)
    print(f"User {user_id}: 결제 전 상품 재고 - {response.json()}")
  except Exception as e:
    print(f"Stock Error : {e}")
    return

  # 주문 생성
  url = "http://localhost:8083/test/purchase-service/purchases"
  headers = {
    "X-USER-ID": str(user_id)
  }

  try:
    body = {
      "productId": product_id,
      "quantity": 1,
      "address": "주소"
    }

    response = requests.post(url, headers=headers, json=body, verify=False)
    print(f"User {user_id}: 주문 ID - ",
          int(response.headers["Location"].split('/')[-1]))
    response_url = response.headers["Location"]
    purchase_id = int(response_url.split("/")[-1])
  except Exception as e:
    print(f"Create Purchase Error : {e}")
    return

  random_num = random.randint(0, 99)
  if random_num < 20:
    url = f"http://localhost:8083/test/purchase-service/purchases/{purchase_id}"
    try:
      response = requests.delete(url, verify=False)
      print(f"Purchase Cancel Finished - ", purchase_id)
      return
    except Exception as e:
      print(f"Cancel Purchase Error : {e}")
      return

  url = "http://localhost:8083/test/payment-service/payments"
  try:
    body = {
      "purchaseId": purchase_id
    }
    response = requests.post(url, headers=headers, json=body, verify=False)
    print(f"User {user_id}: 결제 - {response.json()}")
  except Exception as e:
    print(f"Payment Error : {e}")
    return


def main():
  user_id = 1
  name = "상품 이름"
  content = "상품 설명"
  price = random.randint(1000, 10000)
  stock = 10
  is_reserved = True
  open_at = (
      datetime.now() + timedelta(days=random.randint(-30, 0))).isoformat()

  product_id = create_reservation_product(user_id, name, content, price, stock,
                                          is_reserved, open_at)

  num_requests = 10000

  with ThreadPoolExecutor(max_workers=100) as executor:
    tasks = [executor.submit(scenario, user_id, product_id) for user_id in
             range(1, num_requests + 1)]

    for future in tasks:
      future.result()


if __name__ == "__main__":
  start_time = time.time()
  main()
  end_time = time.time()

  execution_time = end_time - start_time
  print("코드 실행 시간:", execution_time, "초")
