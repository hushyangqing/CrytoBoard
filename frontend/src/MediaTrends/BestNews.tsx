import React, { useEffect, useState } from 'react';
import './BestNews.css'
import axios from "axios";
import {host} from "../Price/Price";

interface BulletProps {
    text: string;
    topPosition: number;
    delay: number;
    bestMedia: string;
}

const Bullet: React.FC<BulletProps> = ({ text, topPosition, delay, bestMedia }) => {
    return (
        <div
            className="bullet"
            style={bestMedia === 'NYTimes' ? {
                top: `${topPosition}%`,
                // animationDelay: `${delay}s`,
                color: 'black'
            }: {
                top: `${topPosition}%`,
                // animationDelay: `${delay}s`,
                color: 'white'
            }}
        >
            {text}
        </div>
    );
};

const BestNews: React.FC = () => {
    const [bullets, setBullets] = useState<BulletProps[]>([]);
    const [currentIndex, setCurrentIndex] = useState(-1);
    const [bestMedia, setBestMedia] = useState<string>('');
    const [bulletMessages, setBulletMessages] = useState<string[]>([]);
    let newBullet: BulletProps;

    useEffect(() => {
        axios.get(`${host}/statistics/bestMedia`)
            .then(response => {
                console.log(response.data);
                setBulletMessages(response.data.articles);
                setBestMedia(response.data.best_source);
                setCurrentIndex(0);
            })
            .catch(error => console.error('Error fetching bestMedia', error));
    }, []);

    useEffect(() => {
        if (currentIndex < 100) {
            console.log("run")
            console.log("bulletMessages.length", bulletMessages.length);
            const interval = setInterval(() => {
                newBullet = {
                    text: bulletMessages[currentIndex],
                    topPosition: Math.random() * 80,
                    delay: Math.random() * 2,
                    bestMedia: bestMedia
                };

                setBullets((prevBullets) => [...prevBullets, newBullet]);
                setCurrentIndex((prevIndex) => (prevIndex + 1) % bulletMessages.length);
            }, 3000 * Math.random());
            return () => clearInterval(interval);
        }
    }, [currentIndex, bestMedia]);

    return (
        <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div className="title"> 🔥 The Most Reflective News Media</div>
            {bestMedia !== 'NYTimes' ? <div className="bullet-screen-fox">
                {bullets.map((bullet, index) => (
                    <Bullet
                        key={index}
                        text={bullet.text}
                        topPosition={bullet.topPosition}
                        delay={bullet.delay}
                        bestMedia={bestMedia}
                    />
                ))}
            </div> : <div className="bullet-screen-nytimes">
                {bullets.map((bullet, index) => (
                    <Bullet
                        key={index}
                        text={bullet.text}
                        topPosition={bullet.topPosition}
                        delay={bullet.delay}
                        bestMedia={bestMedia}
                    />
                ))}
            </div>}

        </div>
    );
};

export default BestNews;
