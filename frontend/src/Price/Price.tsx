import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface CryptoData {
    name: string;
    price: number;
    symbol: string;
}

function Price() {
    // State to hold price data
    const [prices, setPrices] = useState<CryptoData[]>([]);

    // Fetch price data from the backend on component mount
    useEffect(() => {
        axios.get('http://127.0.0.1:5000/top10_current_prices')
            .then(response => setPrices(response.data))
            .catch(error => console.error('Error fetching price data:', error));
    }, []);

    return (
        <div>
            <h2>Top 10 Cryptocurrency Prices</h2>
            <table>
                <thead>
                    <tr>
                        <th>Number</th>
                        <th>Crypto Name</th>
                        <th>Crypto Price</th>
                        <th>Last 24h Graph</th>
                    </tr>
                </thead>
                <tbody>
                    {prices.map((crypto, index) => (
                        <tr key={crypto.symbol}>
                            <td>{index + 1}</td>
                            <td>{crypto.name}</td>
                            <td>${crypto.price.toFixed(2)}</td>
                            <td>Last 24 hour diagram</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Price;
