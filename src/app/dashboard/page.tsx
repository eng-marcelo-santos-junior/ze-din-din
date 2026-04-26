const metrics = [
  {
    label: "Saldo do mês",
    value: "R$ 2.345,67",
    change: "+R$ 345,67",
    positive: true,
    icon: (
      <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a2.25 2.25 0 00-2.25-2.25H15a3 3 0 11-6 0H5.25A2.25 2.25 0 003 12m18 0v6a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 18v-6m18 0V9M3 12V9m18 0a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 9m18 0V6a2.25 2.25 0 00-2.25-2.25H5.25A2.25 2.25 0 003 6v3" />
      </svg>
    ),
    accent: "bg-brand-950",
  },
  {
    label: "Receitas",
    value: "R$ 5.800,00",
    change: "+12% vs. mês anterior",
    positive: true,
    icon: (
      <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
      </svg>
    ),
    accent: "bg-brand-800",
  },
  {
    label: "Despesas",
    value: "R$ 3.454,33",
    change: "-8% vs. mês anterior",
    positive: false,
    icon: (
      <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6L9 12.75l4.286-4.286a11.948 11.948 0 014.306 6.43l.776 2.898m0 0l3.182-5.511m-3.182 5.51l-5.511-3.181" />
      </svg>
    ),
    accent: "bg-red-500",
  },
  {
    label: "Orçamento restante",
    value: "R$ 1.545,67",
    change: "73% utilizado",
    positive: true,
    icon: (
      <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    accent: "bg-brand-500",
  },
];

const categories = [
  { name: "Alimentação", spent: 890, limit: 1000, color: "bg-brand-500" },
  { name: "Moradia",     spent: 1200, limit: 1200, color: "bg-brand-800" },
  { name: "Transporte",  spent: 320, limit: 400,  color: "bg-blue-400" },
  { name: "Lazer",       spent: 480, limit: 300,  color: "bg-red-400" },
  { name: "Saúde",       spent: 220, limit: 400,  color: "bg-amber-400" },
];

const transactions = [
  { description: "Supermercado Pão de Açúcar", category: "Alimentação", date: "Hoje", amount: -287.50 },
  { description: "Conta de luz",               category: "Moradia",     date: "Ontem", amount: -189.50 },
  { description: "Freelance design",           category: "Renda",       date: "22 abr", amount: 1500.00 },
  { description: "Posto de gasolina",          category: "Transporte",  date: "21 abr", amount: -180.00 },
  { description: "Cinema",                     category: "Lazer",       date: "20 abr", amount: -85.00 },
];

const monthlyBars = [
  { month: "Nov", income: 5200, expense: 3800 },
  { month: "Dez", income: 6100, expense: 4900 },
  { month: "Jan", income: 5400, expense: 3200 },
  { month: "Fev", income: 5100, expense: 3600 },
  { month: "Mar", income: 5600, expense: 3100 },
  { month: "Abr", income: 5800, expense: 3454, current: true },
];

const maxBar = 7000;

function fmt(value: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
}

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold text-brand-950">Olá, Marcelo 👋</h1>
          <p className="text-sm text-brand-800/60 mt-0.5">Abril de 2026 · visão geral</p>
        </div>
        <button className="self-start sm:self-auto flex items-center gap-2 rounded-lg bg-brand-800 px-4 py-2 text-sm font-medium text-white hover:bg-brand-950 transition-colors">
          <svg fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Nova transação
        </button>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {metrics.map((m) => (
          <div key={m.label} className="rounded-2xl bg-white p-5 shadow-sm border border-brand-200/40">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-medium text-brand-800/60">{m.label}</span>
              <span className={`${m.accent} rounded-lg p-2 text-white`}>{m.icon}</span>
            </div>
            <p className="text-2xl font-bold text-brand-950">{m.value}</p>
            <p className={`text-xs mt-1 font-medium ${m.positive ? "text-brand-500" : "text-red-500"}`}>
              {m.change}
            </p>
          </div>
        ))}
      </div>

      {/* Middle row */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Monthly evolution chart */}
        <div className="lg:col-span-3 rounded-2xl bg-white p-6 shadow-sm border border-brand-200/40">
          <h2 className="text-sm font-semibold text-brand-950 mb-6">Evolução mensal</h2>
          <div className="flex items-end gap-3 h-40">
            {monthlyBars.map((b) => (
              <div key={b.month} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full flex items-end gap-0.5 h-32">
                  <div
                    className={`flex-1 rounded-t-md transition-all ${b.current ? "bg-brand-800" : "bg-brand-200"}`}
                    style={{ height: `${(b.income / maxBar) * 100}%` }}
                    title={`Receita: ${fmt(b.income)}`}
                  />
                  <div
                    className={`flex-1 rounded-t-md ${b.current ? "bg-red-400" : "bg-red-200"}`}
                    style={{ height: `${(b.expense / maxBar) * 100}%` }}
                    title={`Despesa: ${fmt(b.expense)}`}
                  />
                </div>
                <span className={`text-xs font-medium ${b.current ? "text-brand-950" : "text-brand-800/40"}`}>
                  {b.month}
                </span>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-4 mt-4">
            <span className="flex items-center gap-1.5 text-xs text-brand-800/60">
              <span className="h-2.5 w-2.5 rounded-sm bg-brand-800 inline-block" /> Receitas
            </span>
            <span className="flex items-center gap-1.5 text-xs text-brand-800/60">
              <span className="h-2.5 w-2.5 rounded-sm bg-red-400 inline-block" /> Despesas
            </span>
          </div>
        </div>

        {/* Category budgets */}
        <div className="lg:col-span-2 rounded-2xl bg-white p-6 shadow-sm border border-brand-200/40">
          <h2 className="text-sm font-semibold text-brand-950 mb-6">Categorias</h2>
          <ul className="space-y-4">
            {categories.map((c) => {
              const pct = Math.min((c.spent / c.limit) * 100, 100);
              const over = c.spent > c.limit;
              return (
                <li key={c.name}>
                  <div className="flex justify-between items-baseline mb-1">
                    <span className="text-sm font-medium text-brand-950">{c.name}</span>
                    <span className={`text-xs font-semibold ${over ? "text-red-500" : "text-brand-800/60"}`}>
                      {fmt(c.spent)} / {fmt(c.limit)}
                    </span>
                  </div>
                  <div className="h-1.5 rounded-full bg-brand-50 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${over ? "bg-red-400" : c.color}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </li>
              );
            })}
          </ul>
        </div>
      </div>

      {/* Recent transactions */}
      <div className="rounded-2xl bg-white shadow-sm border border-brand-200/40 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-brand-200/40">
          <h2 className="text-sm font-semibold text-brand-950">Transações recentes</h2>
          <a href="/dashboard/transacoes" className="text-xs font-medium text-brand-800 hover:text-brand-950 transition-colors">
            Ver todas →
          </a>
        </div>
        <ul className="divide-y divide-brand-200/30">
          {transactions.map((t, i) => (
            <li key={i} className="flex items-center gap-4 px-6 py-3.5 hover:bg-brand-50 transition-colors">
              {/* Colored dot */}
              <span
                className={`h-8 w-8 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0 ${
                  t.amount > 0 ? "bg-brand-500" : "bg-brand-200"
                }`}
              >
                {t.amount > 0 ? "+" : "-"}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-brand-950 truncate">{t.description}</p>
                <p className="text-xs text-brand-800/50">{t.category} · {t.date}</p>
              </div>
              <span
                className={`text-sm font-semibold tabular-nums shrink-0 ${
                  t.amount > 0 ? "text-brand-500" : "text-brand-950"
                }`}
              >
                {t.amount > 0 ? "+" : ""}
                {fmt(t.amount)}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
