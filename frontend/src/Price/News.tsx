import './News.css'
import axios from "axios";
import React, {useEffect, useState, useContext, useMemo} from "react";
import {Context} from "../App";

interface NewsProps {
    crypto: string
}

interface NewsState {
    headline: string;
    source: string;
    timestamp: number;
    url: string;
    image_url: string;
    title: string;
}

const nameMapping: { [key: string]: string } = {'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'USDT': 'Tether',
    'BNB': 'BNB',
    'SOL': 'Solana',
    'USDC': 'USDC',
    'XRP': 'XRP',
    'DOGE': 'Dogecoin',
    'TRX': 'TRON',
    'TON': 'Toncoin',
    'ADA': 'Cardano',
    'SHIB': 'Shiba Inu',
    'AVAX': 'Avalanche',
    'BCH': 'Bitcoin Cash',
    'LINK': 'Chainlink',
    'DOT': 'Polkadot',
    'LEO': 'UNUS SED LEO',
    'SUI': 'Sui',
    'DAI': 'Dai',
    'LTC': 'Litecoin'}

function News({crypto}: NewsProps): JSX.Element {

    const [news, setNews] = useState<NewsState[]>([])

    const context = useContext(Context);

    if (!context) {
        throw new Error('No context provided');
    }

    const { setShowPop } = context;

    useEffect(() => {
        axios.get(`http://127.0.0.1:5000/news/search?crypto_name=${crypto}`)
            .then(response => setNews(response.data))
            .catch(error => console.error(`Error fetching news for ${crypto}:`, error));
    }, []);

    const singlePiece = (data: NewsState) => {
        const date = new Date(data.timestamp * 1000);
        // console.log(data.timestamp);
        const formattedDate = date.toLocaleDateString('en-US', {
            month: 'short',  // 缩写月份
            day: 'numeric',  // 日期
            year: 'numeric', // 年份
        });

        return <div className="wholePiece">
            <img className="newsImage" src={data.image_url || '/defaultNews.png'} alt="img"/>
            <div className="singlePiece">
                <div className="singlePieceTitle">
                    <a href={data.url}>{data.title}</a>
                    <span style={{fontSize: "calc(1vw - 5px)", fontWeight: "bold", marginLeft: "4px"}}>{formattedDate}</span>
                    <span style={{fontSize: "calc(1vw - 5px)", marginLeft: "4px"}}>from {data.source}</span>
                </div>
                <div className="singlePieceContent">{data.headline}</div>
                <div className="dividerSub"/>
            </div>
        </div>
    }

    return (<div className="background">
    <div className="newsBox">
            <div className="newsTitle">
                <div className="newsTitleName">Top News of {nameMapping[crypto]}</div>
                <div className="newsTitleCrypto">{crypto}</div>
                <div className="close" onClick={() => setShowPop(undefined)}>X</div>
            </div>
            <div className="titleBackground"/>
            <div className="divider"/>
            {news.map((data) => singlePiece(data))}
        </div>
    </div>);
}

function areEqual(prevProps: { crypto: any; }, nextProps: { crypto: any; }) {
    return prevProps.crypto === nextProps.crypto;
}

export default React.memo(News, areEqual);