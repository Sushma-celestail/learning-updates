def decide_route(state):

    grade = str(state.grade).lower()

    avg_score = float(state.avg_score or 0.0)

    source = state.source

    print("\n========== ROUTE ==========")
    print("GRADE:", grade)
    print("AVG SCORE:", avg_score)
    print("SOURCE:", source)
    print("===========================\n")

    # =========================
    # RELEVANT
    # =========================

    if grade == "relevant":
        return "generate"

    # =========================
    # LOOP CAP
    # =========================

    if state.iterations >= 3:
        print("LOOP CAP REACHED -> generate")
        return "generate"

    # =========================
    # IRRELEVANT (Trigger Web Search)
    # =========================

    return "rewrite"