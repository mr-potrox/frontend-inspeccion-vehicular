import React from "react";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost"| "back";
};

export default function Button({
  variant = "primary",
  className = "",
  ...rest
}: Props) {
  const base =
    "px-4 py-2 rounded-xl text-sm font-medium transition transform active:scale-95";
  const styles: Record<string, string> = {
    primary: "bg-primary text-white hover:bg-primary/90 shadow",
    secondary: "bg-white border text-gray-800 hover:bg-gray-50",
    ghost: "bg-transparent text-gray-700",
    back: "bg-gray-200 text-gray-700 hover:bg-gray-300 shadow-inner",
  };

  return <button className={`${base} ${styles[variant]} ${className}`} {...rest} />;
}