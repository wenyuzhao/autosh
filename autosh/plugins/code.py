from agentia.plugins import tool, Plugin
from typing import Annotated
import traceback
from rich.syntax import Syntax
from rich.console import group
from contextlib import redirect_stdout, redirect_stderr
import io
from . import confirm, code_preview_banner, code_result_panel


@group()
def code_with_explanation(code: str, explanation: str):
    yield Syntax(code.strip(), "python")
    yield "\n[dim]───[/dim]\n"
    yield f"[dim]{explanation}[/dim]"


class CodePlugin(Plugin):
    @tool(
        metadata={
            "banner": code_preview_banner(
                title="Run Python",
                short="[bold]RUN[/bold] [italic]Python Code[/italic]",
                content=lambda a: code_with_explanation(
                    a.get("python_code", ""), a.get("explanation", "")
                ),
            )
        }
    )
    def execute(
        self,
        python_code: Annotated[str, "The python code to run."],
        explanation: Annotated[
            str, "Explain what this code does, and what are you going to use it for."
        ],
    ):
        """
        Execute python code and return the result.
        The python code must be a valid python source file that accepts no inputs.
        Print results to stdout or stderr.
        """
        if not confirm("Execute this code?"):
            return {"error": "The user declined to execute the command."}

        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out):
            with redirect_stderr(err):
                try:
                    exec(python_code, globals())
                    o = out.getvalue()
                    e = err.getvalue()
                    title = "[green][bold]✔[/bold] Finished[/green]"
                    result = {
                        "stdout": o,
                        "stderr": e,
                        "success": True,
                    }
                except Exception as ex:
                    o = out.getvalue()
                    e = err.getvalue()
                    title = "[red][bold]✘[/bold] Failed [/red]"
                    result = {
                        "stdout": o,
                        "stderr": e,
                        "success": False,
                        "error": str(ex),
                        "traceback": repr(traceback.format_exc()),
                    }

        code_result_panel(title, o, e)
        return result
