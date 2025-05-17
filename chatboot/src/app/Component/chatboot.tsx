'use client';

import { useState, useRef, useEffect } from 'react';
import Head from 'next/head';
import styles from '../styles/Chatbot.module.css';

export default function ChatbotPage() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Salut ! Quel est ton identifiant utilisateur ? (ex: u001)' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const messageContent = inputValue.trim();
    const userMessage = { role: 'user', content: messageContent };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      let payload;

      if (/^u\d{3}$/i.test(messageContent)) {
        setUserId(messageContent.toLowerCase());
        payload = { user_id: messageContent.toLowerCase() };
      } else if (userId) {
        payload = { message: messageContent };
      } else {
        payload = {
          preferences: messageContent.toLowerCase().split(',').map(s => s.trim())
        };
      }

      const response = await fetch('http://localhost:3300/loisir', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (data.activites) {
        if (data.activites.length > 0) {
          const reply = data.activites.map(a => `🎯 ${a.titre} — ${a.type} à ${a.lieu}`).join('\n');
          setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
        } else {
          setMessages((prev) => [...prev, { role: 'assistant', content: data.erreur || "Aucune sortie trouvée." }]);
        }
      } else if (data.message) {
        setMessages((prev) => [...prev, { role: 'assistant', content: data.message }]);
      } else if (data.erreur) {
        setMessages((prev) => [...prev, { role: 'assistant', content: data.erreur }]);
      } else {
        setMessages((prev) => [...prev, {
          role: 'assistant',
          content: "Réponse inattendue du serveur."
        }]);
      }

    } catch (error) {
      console.error("Erreur:", error);
      setMessages((prev) => [...prev, {
        role: 'assistant',
        content: "❌ Une erreur est survenue lors de la récupération des suggestions."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Head>
        <title>LoisirBot</title>
        <meta name="description" content="Chatbot de recommandations de sorties" />
      </Head>

      <header className={styles.header}>
        <h1>🤖 LoisirBot IA</h1>
        <p>Découvre des idées de sorties personnalisées !</p>
      </header>

      <div className={styles.chatContainer}>
        <div className={styles.messages}>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`${styles.message} ${message.role === 'user' ? styles.userMessage : styles.assistantMessage}`}
            >
              <div className={styles.messageContent}>
                {message.content.split('\n').map((line, i) => <p key={i}>{line}</p>)}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className={`${styles.message} ${styles.assistantMessage}`}>
              <div className={styles.messageContent}>
                <div className={styles.typingIndicator}>
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className={styles.inputForm}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={!userId ? "Identifiant utilisateur (ex: u001)" : "Parle-moi de tes envies de sorties..."}
            className={styles.inputField}
            disabled={isLoading}
          />
          <button type="submit" className={styles.submitButton} disabled={isLoading}>Envoyer</button>
        </form>
      </div>
    </div>
  );
}
