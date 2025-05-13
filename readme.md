# POST-QUANTUM BLOCKCHAIN
PQB là công nghệ blockchain an toàn kết hợp mật mã hậu lượng tử và công nghệ blockchain với nhau. Điều này có nghĩa là PQB không chỉ có những ưu điểm của blockchain mà còn có thể chống lại các cuộc tấn công của máy tính lượng tử một cách hiệu quả. Chúng tôi cho rằng PQB phải đáp ứng bốn điều kiện sau.
- PQB là sự kết hợp của mật mã hậu lượng tử và công nghệ blockchain;
- PQB có khả năng chống lại các phương pháp tấn công cổ điển đã biết;
- PQB có khả năng chống lại thuật toán lượng tử đã biết các cuộc tấn công như thuật toán Shor, thuật toán Grover;
- Sơ đồ chữ ký trong PQB có tính chất có thể liên kết hoặc theo dõi được. 

-> Vì vậy việc tích hợp chữ ký số dựa trên hàm băm SPHINCS⁺ cho đồng tiền ảo dựa trên công nghệ blockchain là hoàn toàn khả thi.

# Cài đặt
Tải mã nguồn:
> git@github.com:Duongguyen/PostQuantumBlockchain.git
 
Cài đặt SPHINCS+:
- Download:

[Chữ ký số SPHINCS+](https://drive.google.com/file/d/1bTESh3lhsHxPxzTKzBAb32d0CAod1gjK/view?usp=drive_link)

- Giải nén file tải về sau đó Copy vào thư mục ./PQB

[Mã băm SPHINCS+](https://drive.google.com/file/d/1MZ-sjhr4BDGDtXKMwiUfQ1knoo7z1hX_/view?usp=sharing)

- Giải nén file tải về sau đó copy vào thư mục ./PQB/menu

- Cài đặt:

B1: Cài đặt một số thư viện
> pip install -r requirements.txt

B2: Tạo cơ sở dữ liệu MyQL [(Hướng dẫn tách cơ sở dữ liệu ra khỏi Server để đảm bảo an toàn)](https://docs.google.com/document/d/1riXgNtbARJtvEuKX_siMhucKpsq39z-jtCKZKlR7hO4/edit?usp=sharing)
> create date block_chain_sphincs
 
B3: Kết nối Server với MySQL
> python manage.py makemigrations

> python manage.py migrate

B4: Chạy chương trình

> python manage.py runserver

