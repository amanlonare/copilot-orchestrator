import asyncio
import sys
from typing import cast

from langchain_core.runnables import RunnableConfig
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from copilot_orchestrator.domain.entities.query import OrchestratorRequest, UserQuery
from copilot_orchestrator.domain.entities.session import Session
from copilot_orchestrator.orchestration.graph import orchestrator_graph
from copilot_orchestrator.orchestration.state import OrchestratorState
from copilot_orchestrator.presentation.api.dependencies import get_services

console = Console()


async def interactive_chat() -> None:
    """Run an interactive chat session in the terminal."""
    welcome_msg = "[bold blue]Copilot Orchestrator CLI[/bold blue]\nType 'exit' or 'quit' to stop."
    console.print(Panel(welcome_msg, title="Welcome"))

    session_id = "cli-session"
    # In a real CLI, we might load history here
    session = Session(session_id=session_id)
    services = get_services()

    while True:
        user_input = Prompt.ask("\n[bold green]You[/bold green]")

        if user_input.lower() in ("exit", "quit"):
            console.print("[yellow]Goodbye![/yellow]")
            break

        if not user_input.strip():
            continue

        with console.status("[bold blue]Orchestrating response...[/bold blue]"):
            try:
                # 1. Prepare Request
                user_query = UserQuery(text=user_input, session_id=session_id)
                request = OrchestratorRequest(query=user_query)

                # 2. Invoke Graph
                initial_state = cast(
                    OrchestratorState,
                    {
                        "request": request,
                        "session": session,
                        "errors": [],
                        "warnings": [],
                    },
                )
                config = cast(RunnableConfig, {"configurable": services})
                final_state = await orchestrator_graph.ainvoke(initial_state, config=config)

                # 3. Update local session state (to maintain history in the REPL)
                session = final_state["session"]

                # 4. Display Result
                answer = final_state.get("answer")
                if answer:
                    console.print(f"\n[bold blue]Copilot:[/bold blue] {answer.content}")
                else:
                    console.print("\n[bold red]Error:[/bold red] No response generated.")

                # 5. Show Citations if any
                if final_state.get("retrieved_result") and final_state["retrieved_result"].items:
                    console.print("\n[dim]Sources:[/dim]")
                    for citation in final_state["retrieved_result"].items:
                        snippet = citation.snippet[:100]
                        source = citation.source_title or "Untitled"
                        console.print(f"  [dim]- {source}: {snippet}...[/dim]")

                if final_state.get("fallback_flag"):
                    fallback_msg = (
                        "[yellow](Note: Fell back to general knowledge/safe response)[/yellow]"
                    )
                    console.print(fallback_msg)

            except Exception as e:
                console.print(f"\n[bold red]System Error:[/bold red] {e}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(interactive_chat())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting...[/yellow]")
