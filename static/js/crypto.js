document.addEventListener("DOMContentLoaded", function () {
    const coinList = document.getElementById("coin-list");

    // WebSocket kết nối đến API dữ liệu (thay thế URL bên dưới bằng WebSocket thật)
    const ws = new WebSocket("wss://stream.binance.com:9443/ws/!ticker@arr");

    ws.onmessage = function (event) {
        const data = JSON.parse(event.data);

        // Chỉ hiển thị một số coin cụ thể
        const coins = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT"];
        const coinLogos = {
            BTCUSDT: "/static/images/bitcoin.png",
            ETHUSDT: "/static/images/eth.png",
            BNBUSDT: "/static/images/bnb.png",
            XRPUSDT: "/static/images/xrp.png",
            SOLUSDT: "/static/images/sol.png",
        };

        coinList.innerHTML = ""; // Xóa nội dung cũ

        data.forEach((coin) => {
            if (coins.includes(coin.s)) {
                const change = parseFloat(coin.P);
                const color = change >= 0 ? "text-success" : "text-danger";

                // Thêm vào danh sách
                const listItem = document.createElement("li");
                listItem.className = "list-group-item d-flex justify-content-between align-items-center";
                listItem.innerHTML = `
                    <div class="d-flex align-items-center">
                        <img src="${coinLogos[coin.s]}" alt="${coin.s}" class="me-2" style="width: 24px; height: 24px;">
                        <span>${coin.s.replace("USDT", "")}</span>
                    </div>
                    <div>
                        <span class="me-3">$${parseFloat(coin.c).toFixed(2)}</span>
                        <span class="${color}">${change.toFixed(2)}%</span>
                    </div>
                `;
                coinList.appendChild(listItem);
            }
        });
    };

    ws.onerror = function (error) {
        console.error("WebSocket Error: ", error);
    };
});
