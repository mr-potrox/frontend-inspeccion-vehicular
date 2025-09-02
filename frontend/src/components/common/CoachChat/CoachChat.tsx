import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function CoachChat({ messages }: { messages: string[] }) {
  const [visible, setVisible] = useState<string[]>([]);
  const [typing, setTyping] = useState(false);

  useEffect(() => {
    setVisible([]);
    let i = 0;
    const t = setInterval(() => {
      if (i < messages.length) {
        setTyping(true);
        setTimeout(() => {
          setVisible((v) => [...v, messages[i++]]);
          setTyping(false);
        }, 500);
      } else clearInterval(t);
    }, 1200);
    return () => clearInterval(t);
  }, [messages]);

  return (
    <div className="space-y-3">
      {visible.map((m, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="flex items-start gap-3"
        >
          <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold">
            A
          </div>
          <div className="bg-white border border-gray-100 rounded-2xl px-4 py-2 shadow text-sm max-w-prose">
            {m}
          </div>
        </motion.div>
      ))}
      {typing && (
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold">
            A
          </div>
          <div className="bg-white border border-gray-100 rounded-2xl px-4 py-2 shadow text-sm max-w-prose italic text-gray-500">
            escribiendo...
          </div>
        </div>
      )}
    </div>
  );
}
