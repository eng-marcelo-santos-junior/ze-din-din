import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import HomePage from "../page";

function getToggle() {
  return within(screen.getByTestId("tab-toggle"));
}

function getSubmitButton() {
  return document.querySelector<HTMLButtonElement>('button[type="submit"]')!;
}

describe("HomePage", () => {
  describe("modo login (padrão)", () => {
    it("renderiza o nome do app", () => {
      render(<HomePage />);
      expect(screen.getByText("Zé Din Din")).toBeInTheDocument();
    });

    it("exibe os 4 cards de funcionalidades", () => {
      render(<HomePage />);
      expect(screen.getByText("Controle total das finanças")).toBeInTheDocument();
      expect(screen.getByText("Categorização inteligente")).toBeInTheDocument();
      expect(screen.getByText("Orçamentos mensais")).toBeInTheDocument();
      expect(screen.getByText("Insights automáticos")).toBeInTheDocument();
    });

    it("exibe o título 'Bem-vindo de volta'", () => {
      render(<HomePage />);
      expect(screen.getByText("Bem-vindo de volta")).toBeInTheDocument();
    });

    it("exibe campos de e-mail e senha", () => {
      render(<HomePage />);
      expect(screen.getByLabelText("E-mail")).toBeInTheDocument();
      expect(screen.getByLabelText("Senha")).toBeInTheDocument();
    });

    it("não exibe o campo Nome", () => {
      render(<HomePage />);
      expect(screen.queryByLabelText("Nome")).not.toBeInTheDocument();
    });

    it("não exibe o campo Confirmar senha", () => {
      render(<HomePage />);
      expect(screen.queryByLabelText("Confirmar senha")).not.toBeInTheDocument();
    });

    it("exibe o link 'Esqueci minha senha'", () => {
      render(<HomePage />);
      expect(screen.getByText("Esqueci minha senha")).toBeInTheDocument();
    });

    it("o botão de submit exibe 'Entrar'", () => {
      render(<HomePage />);
      expect(getSubmitButton()).toHaveTextContent("Entrar");
    });
  });

  describe("alternância de modo", () => {
    it("muda para modo cadastro ao clicar na aba 'Criar conta'", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      await user.click(getToggle().getByRole("button", { name: "Criar conta" }));

      expect(screen.getByText("Comece agora")).toBeInTheDocument();
    });

    it("exibe campos adicionais no modo cadastro", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      await user.click(getToggle().getByRole("button", { name: "Criar conta" }));

      expect(screen.getByLabelText("Nome")).toBeInTheDocument();
      expect(screen.getByLabelText("Confirmar senha")).toBeInTheDocument();
    });

    it("oculta 'Esqueci minha senha' no modo cadastro", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      await user.click(getToggle().getByRole("button", { name: "Criar conta" }));

      expect(screen.queryByText("Esqueci minha senha")).not.toBeInTheDocument();
    });

    it("o botão de submit exibe 'Criar conta' no modo cadastro", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      await user.click(getToggle().getByRole("button", { name: "Criar conta" }));

      expect(getSubmitButton()).toHaveTextContent("Criar conta");
    });

    it("retorna ao modo login ao clicar na aba 'Entrar'", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      await user.click(getToggle().getByRole("button", { name: "Criar conta" }));
      await user.click(getToggle().getByRole("button", { name: "Entrar" }));

      expect(screen.getByText("Bem-vindo de volta")).toBeInTheDocument();
    });

    it("retorna ao modo login ao clicar no link 'Entrar' do rodapé", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      await user.click(getToggle().getByRole("button", { name: "Criar conta" }));

      await user.click(screen.getByTestId("footer-switch"));

      expect(screen.getByText("Bem-vindo de volta")).toBeInTheDocument();
    });
  });

  describe("interação com o formulário", () => {
    it("atualiza o campo e-mail ao digitar", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      const emailInput = screen.getByLabelText("E-mail");
      await user.type(emailInput, "teste@email.com");

      expect(emailInput).toHaveValue("teste@email.com");
    });

    it("atualiza o campo senha ao digitar", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      const passwordInput = screen.getByLabelText("Senha");
      await user.type(passwordInput, "senha123");

      expect(passwordInput).toHaveValue("senha123");
    });

    it("atualiza o campo nome ao digitar no modo cadastro", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      await user.click(getToggle().getByRole("button", { name: "Criar conta" }));

      const nameInput = screen.getByLabelText("Nome");
      await user.type(nameInput, "Maria");

      expect(nameInput).toHaveValue("Maria");
    });

    it("não reseta os campos ao alternar de modo", async () => {
      const user = userEvent.setup();
      render(<HomePage />);

      await user.type(screen.getByLabelText("E-mail"), "teste@email.com");

      await user.click(getToggle().getByRole("button", { name: "Criar conta" }));
      await user.click(getToggle().getByRole("button", { name: "Entrar" }));

      expect(screen.getByLabelText("E-mail")).toHaveValue("teste@email.com");
    });
  });
});
