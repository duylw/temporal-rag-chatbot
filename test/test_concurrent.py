import asyncio
import httpx
import time

async def send_request(client, question_number):
    if question_number % 2 == 0:
        question = "giải thích cơ chế hoạt động của self-attention trong kiến trúc transformer"
    else:
        question = "tóm tắt các biến thể của RNNsv và vấn đề chúng đã giải quyết"
    url = f"http://localhost:8000/agentic_ask/?question={question}"
    print(f"-> Đang gửi request {question_number}...")
    
    start_time = time.time()
    response = await client.post(url)
    duration = time.time() - start_time
    
    print(f"<- Nhận response cho câu hỏi {question_number} "
          f"(Status: {response.status_code}, Time: {duration:.2f}s)")

async def main():
    # Giả sử bạn muốn gửi 10 request cùng một lúc
    NUM_REQUESTS = 10
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        tasks = []
        for i in range(1, NUM_REQUESTS + 1):
            tasks.append(send_request(client, i))
            
        # asyncio.gather sẽ chạy tất cả các request cùng một lúc
        print(f"Bắt đầu gửi {NUM_REQUESTS} requests...")
        await asyncio.gather(*tasks)
        print("Đã hoàn tất tất cả requests!")

if __name__ == "__main__":
    asyncio.run(main())