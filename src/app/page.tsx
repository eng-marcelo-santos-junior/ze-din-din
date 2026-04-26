"use client";

import { useState } from "react";

const features = [
  {
    icon: "📊",
    title: "Controle total das finanças",
    description: "Registre receitas e despesas e veja em tempo real quanto sobra no mês.",
  },
  {
    icon: "🏷️",
    title: "Categorização inteligente",
    description: "Organize seus gastos por categoria e entenda para onde vai seu dinheiro.",
  },
  {
    icon: "🎯",
    title: "Orçamentos mensais",
    description: "Defina limites por categoria e receba alertas antes de estourar.",
  },
  {
    icon: "📈",
    title: "Insights automáticos",
    description: "Receba sugestões baseadas no seu histórico para economizar mais.",
  },
];

export default function HomePage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "" });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // TODO: integrate with auth API
  }

  return (
    <div className="min-h-screen bg-brand-50 flex flex-col lg:flex-row">
      {/* Left — presentation */}
      <div className="lg:w-1/2 bg-brand-950 text-white flex flex-col justify-center px-10 py-16 lg:px-16">
        <div className="max-w-lg">
          <div className="flex items-center gap-3 mb-10">
            <span className="text-4xl">🌿</span>
            <h1 className="text-3xl font-bold tracking-tight">Zé Din Din</h1>
          </div>

          <p className="text-xl font-medium text-brand-200 mb-3">
            Finanças simples para uma vida melhor.
          </p>
          <p className="text-brand-200/70 mb-12 leading-relaxed">
            Acompanhe receitas, despesas e orçamentos em um só lugar — sem planilhas complicadas, sem
            jargão financeiro.
          </p>

          <ul className="space-y-6">
            {features.map((f) => (
              <li key={f.title} className="flex gap-4 items-start">
                <span className="text-2xl mt-0.5">{f.icon}</span>
                <div>
                  <p className="font-semibold text-white">{f.title}</p>
                  <p className="text-brand-200/70 text-sm mt-0.5 leading-relaxed">{f.description}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Right — auth form */}
      <div className="lg:w-1/2 flex items-center justify-center px-6 py-16">
        <div className="w-full max-w-md">
          {/* Tab toggle */}
          <div data-testid="tab-toggle" className="flex rounded-xl bg-brand-200/30 p-1 mb-8">
            <button
              onClick={() => setMode("login")}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
                mode === "login"
                  ? "bg-white text-brand-950 shadow-sm"
                  : "text-brand-800/60 hover:text-brand-800"
              }`}
            >
              Entrar
            </button>
            <button
              onClick={() => setMode("register")}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${
                mode === "register"
                  ? "bg-white text-brand-950 shadow-sm"
                  : "text-brand-800/60 hover:text-brand-800"
              }`}
            >
              Criar conta
            </button>
          </div>

          <h2 className="text-2xl font-bold text-brand-950 mb-1">
            {mode === "login" ? "Bem-vindo de volta" : "Comece agora"}
          </h2>
          <p className="text-brand-800/60 text-sm mb-8">
            {mode === "login"
              ? "Entre na sua conta para continuar."
              : "Crie sua conta gratuita em segundos."}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "register" && (
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-brand-950/70 mb-1">
                  Nome
                </label>
                <input
                  id="name"
                  name="name"
                  type="text"
                  required
                  placeholder="Seu nome"
                  value={form.name}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-brand-200 px-4 py-2.5 text-sm text-brand-950 placeholder-brand-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                />
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-brand-950/70 mb-1">
                E-mail
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                placeholder="seu@email.com"
                value={form.email}
                onChange={handleChange}
                className="w-full rounded-lg border border-brand-200 px-4 py-2.5 text-sm text-brand-950 placeholder-brand-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-brand-950/70 mb-1">
                Senha
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
                className="w-full rounded-lg border border-brand-200 px-4 py-2.5 text-sm text-brand-950 placeholder-brand-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>

            {mode === "register" && (
              <div>
                <label
                  htmlFor="confirmPassword"
                  className="block text-sm font-medium text-brand-950/70 mb-1"
                >
                  Confirmar senha
                </label>
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  required
                  placeholder="••••••••"
                  value={form.confirmPassword}
                  onChange={handleChange}
                  className="w-full rounded-lg border border-brand-200 px-4 py-2.5 text-sm text-brand-950 placeholder-brand-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                />
              </div>
            )}

            {mode === "login" && (
              <div className="text-right">
                <a href="#" className="text-sm text-brand-800 hover:text-brand-950 font-medium">
                  Esqueci minha senha
                </a>
              </div>
            )}

            <button
              type="submit"
              className="w-full bg-brand-800 hover:bg-brand-950 text-white font-semibold py-2.5 rounded-lg transition-colors mt-2"
            >
              {mode === "login" ? "Entrar" : "Criar conta"}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-brand-800/60">
            {mode === "login" ? (
              <>
                Não tem conta?{" "}
                <button
                  onClick={() => setMode("register")}
                  className="text-brand-800 hover:text-brand-950 font-medium"
                >
                  Cadastre-se grátis
                </button>
              </>
            ) : (
              <>
                Já tem conta?{" "}
                <button
                  data-testid="footer-switch"
                  onClick={() => setMode("login")}
                  className="text-brand-800 hover:text-brand-950 font-medium"
                >
                  Entrar
                </button>
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
