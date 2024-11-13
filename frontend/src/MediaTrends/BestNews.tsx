import React, { useEffect, useState } from 'react';
import './BestNews.css'

const bulletMessages = [
    "Hello, World!",
    "This is a bullet message!",
    "React is awesome!",
    "Enjoy the animation!",
    "TypeScript and React rocks!",
    "Keep watching!"
];

interface BulletProps {
    text: string;
    topPosition: number;
    delay: number;
}

const Bullet: React.FC<BulletProps> = ({ text, topPosition, delay }) => {
    return (
        <div
            className="bullet"
            style={{
                top: `${topPosition}%`,
                animationDelay: `${delay}s`
            }}
        >
            {text}
        </div>
    );
};

const BestNews: React.FC = () => {
    const [bullets, setBullets] = useState<BulletProps[]>([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    let newBullet: BulletProps;

    useEffect(() => {
        const interval = setInterval(() => {
            newBullet = {
                text: bulletMessages[currentIndex],
                topPosition: Math.random() * 80,
                delay: Math.random()
            };

            setBullets((prevBullets) => [...prevBullets, newBullet]);
            setCurrentIndex((prevIndex) => (prevIndex + 1) % bulletMessages.length);
        }, 2000);

        return () => clearInterval(interval);
    }, [currentIndex]);

    return (
        <div className="bullet-screen">
            {bullets.map((bullet, index) => (
                <Bullet
                    key={index}
                    text={bullet.text}
                    topPosition={bullet.topPosition}
                    delay={bullet.delay}
                />
            ))}
        </div>
    );
};

export default BestNews;
