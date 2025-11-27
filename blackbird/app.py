import gradio as gr
from util import css, js, Color
import pandas as pd
from trading_floor import names, lastnames, short_model_names
import plotly.express as px
from accounts import Account
from database import read_log

mapper = {
    "trace": Color.WHITE,
    "agent": Color.CYAN,
    "function": Color.GREEN,
    "generation": Color.YELLOW,
    "response": Color.MAGENTA,
    "account": Color.RED,
}


class Trader:
    def __init__(self, name: str, lastname: str, model_name: str):
        self.name = name
        self.lastname = lastname
        self.model_name = model_name
        self.account = Account.get(name)

    def reload(self):
        self.account = Account.get(self.name)

    def get_title(self) -> str:
        return f"<div style='text-align: center;font-size:34px;'>{self.name}<span style='color:#ccc;font-size:24px;'> ({self.model_name}) - {self.lastname}</span></div>"

    def get_strategy(self) -> str:
        return self.account.get_strategy()

    def get_portfolio_value_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self.account.portfolio_value_time_series, columns=["datetime", "value"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df

    def get_portfolio_value_chart(self):
        df = self.get_portfolio_value_df()
        fig = px.line(df, x="datetime", y="value")
        margin = dict(l=40, r=20, t=20, b=40)
        fig.update_layout(
            height=300,
            margin=margin,
            xaxis_title=None,
            yaxis_title=None,
            paper_bgcolor="#bbb",
            plot_bgcolor="#dde",
        )
        fig.update_xaxes(tickformat="%m/%d", tickangle=45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=8), tickformat=",.0f")
        return fig

    def get_holdings_df(self) -> pd.DataFrame:
        holdings = self.account.get_holdings()
        if not holdings:
            return pd.DataFrame(columns=["Symbol", "Quantity"])
        return pd.DataFrame([{"Symbol": s, "Quantity": q} for s, q in holdings.items()])

    def get_transactions_df(self) -> pd.DataFrame:
        tx = self.account.list_transactions()
        if not tx:
            return pd.DataFrame(columns=["Timestamp", "Symbol", "Quantity", "Price", "Rationale"])
        return pd.DataFrame(tx)

    def get_portfolio_value(self) -> str:
        value = self.account.calculate_portfolio_value() or 0.0
        pnl = self.account.calculate_profit_loss(value) or 0.0
        color = "green" if pnl >= 0 else "red"
        emoji = "up" if pnl >= 0 else "down"
        return f"<div style='text-align:center;background:{color};padding:10px;'><span style='font-size:32px'>${value:,.0f}</span> <span style='font-size:24px'>{emoji} ${pnl:,.0f}</span></div>"

    def get_logs(self, previous=None) -> str:
        logs = read_log(self.name, last_n=13)
        lines = ""
        for ts, typ, msg in logs:
            col = mapper.get(typ, Color.WHITE).value
            lines += f"<span style='color:{col}'>{ts} : [{typ}] {msg}</span><br/>"
        html = f"<div style='height:250px;overflow-y:auto'>{lines}</div>"
        return html if html != previous else gr.update()


class TraderView:
    def __init__(self, trader: Trader):
        self.trader = trader
        self.portfolio_value = None
        self.chart = None
        self.holdings = None
        self.transactions = None
        self.log = None

    def make_ui(self):
        with gr.Column():
            gr.HTML(self.trader.get_title())
            with gr.Row():
                self.portfolio_value = gr.HTML(self.trader.get_portfolio_value)
            with gr.Row():
                self.chart = gr.Plot(self.trader.get_portfolio_value_chart, show_label=False)
            with gr.Row(variant="panel"):
                self.log = gr.HTML(self.trader.get_logs)
            with gr.Row():
                self.holdings = gr.Dataframe(
                    self.trader.get_holdings_df,
                    label="Holdings",
                    headers=["Symbol", "Quantity"],
                    row_count=(5, "dynamic"),
                    max_height=300,
                )
            with gr.Row():
                self.transactions = gr.Dataframe(
                    self.trader.get_transactions_df,
                    label="Recent Transactions",
                    headers=["Timestamp", "Symbol", "Quantity", "Price", "Rationale"],
                    row_count=(5, "dynamic"),
                    max_height=300,
                )

        gr.Timer(120).tick(
            self.refresh,
            outputs=[self.portfolio_value, self.chart, self.holdings, self.transactions],
        )
        gr.Timer(0.5).tick(
            self.trader.get_logs,
            inputs=self.log,
            outputs=self.log,
        )

    def refresh(self):
        self.trader.reload()
        return (
            self.trader.get_portfolio_value(),
            self.trader.get_portfolio_value_chart(),
            self.trader.get_holdings_df(),
            self.trader.get_transactions_df(),
        )


def create_ui():
    traders = [Trader(n, l, m) for n, l, m in zip(names, lastnames, short_model_names)]
    views = [TraderView(t) for t in traders]

    with gr.Blocks() as ui:
        gr.HTML(f"<style>{css}</style>")
        if js:
            gr.HTML(f"<script>{js}</script>")

        with gr.Row():
            for v in views:
                v.make_ui()

    return ui


if __name__ == "__main__":
    ui = create_ui()
    ui.launch(inbrowser=True)