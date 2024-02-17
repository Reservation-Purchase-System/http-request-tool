import random
from datetime import datetime, timedelta

import requests


def create_reservation_product(user_id, name, content, price, stock, reserved_at):
  api_endpoint = "http://localhost:8083/product-service/reservation-products"

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
    "reservedAt": reserved_at
  }

  # 상품 생성 API 호출
  response = requests.post(api_endpoint, headers=headers, json=request_body)

  # 응답 확인
  if response.status_code == 201:
    print("상품 생성 성공")
    print("생성된 상품 ID:", response.headers["Location"])  # 생성된 상품 ID 확인
  else:
    print("상품 생성 실패:", response.text)


def main():
  # 예약 상품 생성
  for _ in range(100):
    user_id = random.randint(1, 101)
    name = "상품 이름"
    content = "상품 설명"
    price = random.randint(1000, 10000)
    stock = random.randint(100, 10000)
    reserved_at = (datetime.now() + timedelta(days=random.randint(-30, 2))).isoformat()

    create_reservation_product(user_id, name, content, price, stock, reserved_at)

if __name__ == "__main__":
  main()
