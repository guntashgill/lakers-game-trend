from preswald import connect, get_df, text, slider, table, plotly
import plotly.express as px
import pandas as pd

connect()
df = get_df("nba_vegas")

if df is not None and not df.empty:
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={"oppteam": "opp_team", "average_line_ou": "avg_ou_line"})

    # Filter to just Lakers games
    team_name = "L.A. Lakers"
    df = df[(df["team"] == team_name) | (df["opp_team"] == team_name)].copy()
    df["date"] = pd.to_datetime(df["date"])
    df["date_str"] = df["date"].astype(str)

    # Title and description
    text(f"# 🏀 {team_name} Game Breakdown (2018–2019)")
    text("A quick look at how the Lakers performed game by game — from overall trends to how they handled tough schedules.")

    # Score filter slider
    min_score = int(df["total"].min())
    max_score = int(df["total"].max())
    score_cutoff = slider("Set a minimum total score to include a game:", min_val=min_score, max_val=max_score, default=min_score)
    df = df[df["total"] >= score_cutoff]

    text(f"### Showing {len(df)} games with total score ≥ {score_cutoff}")

    # Scoring trend line chart
    text("## Scoring Trend Over Time")
    fig_line = px.line(
        df,
        x="date_str",
        y="total",
        title="Total Points by Game Date",
        labels={"total": "Points", "date_str": "Game Date"},
        color_discrete_sequence=["#552583"]  # Lakers purple
    )
    plotly(fig_line)

    # Top 10 scoring games table
    text("## Top 10 Highest-Scoring Games")
    table(df[["date_str", "team", "opp_team", "total"]].head(10).astype(str).to_dict("records"), title="Highest Scoring Games")

    # Avg points vs opponents
    df["opponent"] = df.apply(lambda row: row["opp_team"] if row["team"] == team_name else row["team"], axis=1)
    avg_by_opp = df.groupby("opponent")["total"].mean().sort_values(ascending=False).reset_index()

    text("## Avg Points Scored vs Each Opponent")
    fig_bar = px.bar(
        avg_by_opp,
        x="opponent",
        y="total",
        title="Lakers Avg Points vs Other Teams",
        labels={"total": "Avg Points", "opponent": "Opponent"},
        color_discrete_sequence=["#FDB927"]  # Lakers gold
    )
    plotly(fig_bar)

    # Monthly trends
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly_avg = df.groupby("month")["total"].mean().reset_index()

    text("## Monthly Scoring Breakdown")
    fig_month = px.bar(
        monthly_avg,
        x="month",
        y="total",
        title="Average Score Per Month",
        labels={"month": "Month", "total": "Avg Points"},
        color_discrete_sequence=["#552583"]  # Lakers purple
    )
    plotly(fig_month)

    # Back-to-back game impact
    df = df.sort_values(by="date")
    df["prev_game_date"] = df["date"].shift(1)
    df["days_since_last_game"] = (df["date"] - df["prev_game_date"]).dt.days
    df["back_to_back"] = df["days_since_last_game"] == 1

    b2b_avg = df.groupby("back_to_back")["total"].mean().reset_index()
    b2b_avg["back_to_back"] = b2b_avg["back_to_back"].replace({True: "Back-to-Back", False: "Rested"})

    text("## Back-to-Back Game Impact")
    text("Did playing two nights in a row have any effect on the Lakers scoring performance?")

    fig_b2b = px.bar(
        b2b_avg,
        x="back_to_back",
        y="total",
        title="Avg Score: Rested vs Back-to-Back",
        labels={"total": "Avg Points", "back_to_back": "Game Type"},
        color_discrete_sequence=["#FDB927", "#552583"]  # Gold and Purple
    )
    plotly(fig_b2b)

else:
    text("⚠️ Couldn't load any Lakers data. Please check your dataset or try reloading.")
