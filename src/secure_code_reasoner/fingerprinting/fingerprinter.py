"""Fingerprinting subsystem implementation."""

import ast
import hashlib
import logging
from pathlib import Path
from typing import Any

from secure_code_reasoner.exceptions import FingerprintingError
from secure_code_reasoner.fingerprinting.models import (
    ClassArtifact,
    CodeArtifact,
    CodeArtifactType,
    DependencyGraph,
    FileArtifact,
    FunctionArtifact,
    RepositoryFingerprint,
    RiskSignal,
)

logger = logging.getLogger(__name__)


class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor for extracting semantic code segments and risk signals."""

    def __init__(self, file_path: Path) -> None:
        """Initialize visitor."""
        self.file_path = file_path
        self.classes: list[ClassArtifact] = []
        self.functions: list[FunctionArtifact] = []
        self.risk_signals: set[RiskSignal] = set()
        self.current_class: str | None = None
        self.imports: set[str] = set()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        base_classes = [self._get_name(base) for base in node.bases]
        methods: set[str] = set()
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                methods.add(item.name)

        class_segment = ClassArtifact(
            artifact_type=CodeArtifactType.CLASS,
            name=node.name,
            path=self.file_path,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            methods=frozenset(methods),
            base_classes=frozenset(base_classes),
            risk_signals=self._extract_class_risk_signals(node),
        )
        self.classes.append(class_segment)

        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        self._visit_function(node, is_async=True)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool) -> None:
        """Process function definition."""
        parameters = [arg.arg for arg in node.args.args]
        return_type = ast.unparse(node.returns) if node.returns else None
        decorators = [ast.unparse(d) for d in node.decorator_list]

        func_segment = FunctionArtifact(
            artifact_type=CodeArtifactType.FUNCTION,
            name=node.name,
            path=self.file_path,
            start_line=node.lineno,
            end_line=node.end_lineno or node.lineno,
            parameters=frozenset(parameters),
            return_type=return_type,
            is_async=is_async,
            decorators=frozenset(decorators),
            risk_signals=self._extract_function_risk_signals(node),
            metadata={"class": self.current_class} if self.current_class else {},
        )
        self.functions.append(func_segment)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit function call to detect risk signals."""
        func_name = self._get_name(node.func)
        self._check_call_risk_signals(func_name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement."""
        for alias in node.names:
            self.imports.add(alias.name)
            if self._is_external_dependency(alias.name):
                self.risk_signals.add(RiskSignal.EXTERNAL_DEPENDENCY)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit import from statement."""
        if node.module:
            self.imports.add(node.module)
            if self._is_external_dependency(node.module):
                self.risk_signals.add(RiskSignal.EXTERNAL_DEPENDENCY)
        self.generic_visit(node)

    def _get_name(self, node: ast.AST) -> str:
        """Extract name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        try:
            return ast.unparse(node)
        except Exception:
            return str(node)

    def _is_external_dependency(self, module_name: str) -> bool:
        """Check if module is an external dependency (not stdlib)."""
        if not module_name:
            return False
        stdlib_modules = {
            "os",
            "sys",
            "json",
            "csv",
            "datetime",
            "time",
            "math",
            "random",
            "collections",
            "itertools",
            "functools",
            "operator",
            "pathlib",
            "typing",
            "dataclasses",
            "enum",
            "abc",
            "contextlib",
            "logging",
            "re",
            "string",
            "struct",
            "hashlib",
            "base64",
            "urllib",
            "http",
            "socket",
            "ssl",
            "subprocess",
            "multiprocessing",
            "threading",
            "asyncio",
            "concurrent",
            "queue",
            "select",
            "signal",
            "tempfile",
            "shutil",
            "glob",
            "fnmatch",
            "io",
            "pickle",
            "copy",
            "weakref",
            "warnings",
            "traceback",
            "inspect",
            "importlib",
            "pkgutil",
            "unittest",
            "doctest",
        }
        return module_name.split(".")[0] not in stdlib_modules

    def _extract_class_risk_signals(self, node: ast.ClassDef) -> frozenset[RiskSignal]:
        """Extract risk signals from class definition."""
        signals: set[RiskSignal] = set()
        for base in node.bases:
            base_name = self._get_name(base)
            if "pickle" in base_name.lower() or "serialize" in base_name.lower():
                signals.add(RiskSignal.DESERIALIZATION)
        return frozenset(signals)

    def _extract_function_risk_signals(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> frozenset[RiskSignal]:
        """Extract risk signals from function definition."""
        signals: set[RiskSignal] = set()
        for decorator in node.decorator_list:
            decorator_name = self._get_name(decorator)
            if "pickle" in decorator_name.lower():
                signals.add(RiskSignal.DESERIALIZATION)
        return frozenset(signals)

    def _check_call_risk_signals(self, func_name: str) -> None:
        """Check function calls for risk signals."""
        func_lower = func_name.lower()
        if any(op in func_lower for op in ["open", "read", "write", "remove", "delete", "unlink"]):
            self.risk_signals.add(RiskSignal.FILE_OPERATIONS)
        if any(
            op in func_lower for op in ["socket", "request", "http", "urllib", "connect", "urlopen"]
        ):
            self.risk_signals.add(RiskSignal.NETWORK_ACCESS)
        if any(
            op in func_lower for op in ["exec", "eval", "compile", "run", "popen", "call", "system"]
        ):
            self.risk_signals.add(RiskSignal.PROCESS_EXECUTION)
        if any(
            op in func_lower
            for op in ["crypto", "hash", "encrypt", "decrypt", "sign", "hmac", "sha", "md5"]
        ):
            self.risk_signals.add(RiskSignal.CRYPTOGRAPHIC_OPERATIONS)
        if any(
            op in func_lower for op in ["pickle", "marshal", "yaml.load", "json.loads", "loads"]
        ):
            self.risk_signals.add(RiskSignal.DESERIALIZATION)
        if any(op in func_lower for op in ["eval", "exec", "__import__"]):
            self.risk_signals.add(RiskSignal.DYNAMIC_CODE_EXECUTION)
        if any(
            op in func_lower
            for op in ["getattr", "setattr", "hasattr", "__getattribute__", "getattribute"]
        ):
            self.risk_signals.add(RiskSignal.REFLECTION)
        if any(op in func_lower for op in ["config", "settings", "env", "getenv", "environ"]):
            self.risk_signals.add(RiskSignal.CONFIGURATION_ACCESS)


class Fingerprinter:
    """Generates deterministic fingerprints of code repositories."""

    SUPPORTED_EXTENSIONS = {".py"}
    IGNORE_DIRS = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".venv",
        "venv",
        "env",
        ".mypy_cache",
        ".ruff_cache",
    }
    IGNORE_FILES = {".gitignore", ".gitattributes", ".DS_Store"}

    def __init__(self, repository_path: Path) -> None:
        """Initialize fingerprinter with repository path."""
        self.repository_path = Path(repository_path).resolve()
        if not self.repository_path.exists():
            raise FingerprintingError(f"Repository path does not exist: {self.repository_path}")
        if not self.repository_path.is_dir():
            raise FingerprintingError(f"Repository path is not a directory: {self.repository_path}")

    def _validate_path_within_root(self, path: Path) -> Path:
        """Validate that resolved path remains within repository root."""
        resolved = path.resolve()
        if not resolved.is_relative_to(self.repository_path):
            raise FingerprintingError(
                f"Resolved path escapes repository root: {resolved} (root: {self.repository_path})"
            )
        return resolved

    def fingerprint(self) -> RepositoryFingerprint:
        """Generate fingerprint for the repository."""
        logger.info(f"Fingerprinting repository: {self.repository_path}")
        artifacts: list[CodeArtifact] = []
        languages: dict[str, int] = {}
        total_lines = 0
        failed_files: list[str] = []

        for file_path in self._walk_repository():
            try:
                file_artifacts, had_syntax_error = self._process_file(file_path)
                artifacts.extend(file_artifacts)
                if had_syntax_error:
                    failed_files.append(file_path.as_posix())

                for artifact in file_artifacts:
                    if isinstance(artifact, FileArtifact):
                        lang = artifact.language or "unknown"
                        languages[lang] = languages.get(lang, 0) + 1
                        total_lines += artifact.line_count
            except (OSError, PermissionError, UnicodeDecodeError) as e:
                logger.warning(f"Failed to process file {file_path}: {e}")
                failed_files.append(file_path.as_posix())
            except FingerprintingError:
                raise  # Propagate fingerprinting errors

        dependency_graph = self._build_dependency_graph(artifacts)

        risk_signals: dict[RiskSignal, int] = {}
        for artifact in artifacts:
            for signal in artifact.risk_signals:
                risk_signals[signal] = risk_signals.get(signal, 0) + 1

        total_files = sum(1 for a in artifacts if isinstance(a, FileArtifact))
        total_classes = sum(1 for a in artifacts if isinstance(a, ClassArtifact))
        total_functions = sum(1 for a in artifacts if isinstance(a, FunctionArtifact))

        artifacts_tuple = tuple(
            sorted(artifacts, key=lambda a: (a.path.as_posix(), a.start_line, a.name))
        )

        # Mitigation B: Never return valid fingerprint on TypeError
        try:
            artifacts_set = frozenset(artifacts_tuple)
        except TypeError as e:
            raise FingerprintingError(
                f"TypeError during fingerprint generation (non-hashable artifacts): {e}. "
                "Fingerprint cannot be generated. This indicates a bug in artifact construction."
            ) from e

        fingerprint_hash = self._compute_fingerprint_hash(artifacts, dependency_graph)

        # Epistemic closure: Explicit status semantics
        # COMPLETE_NO_SKIPS: All processable files processed successfully, no intentional skips
        # COMPLETE_WITH_SKIPS: All processable files processed successfully, but some files intentionally skipped
        # PARTIAL: Some processable files failed to process
        # FAILED: Fingerprinting failed entirely
        if failed_files:
            fingerprint_status = "PARTIAL"
            status_metadata = {
                "failed_files": sorted(failed_files),
                "failed_file_count": len(failed_files),
            }
        else:
            # Note: Intentional skips (IGNORE_DIRS, IGNORE_FILES, non-.py) are always present
            # This is COMPLETE_WITH_SKIPS by design (skips are intentional, not failures)
            fingerprint_status = "COMPLETE_WITH_SKIPS"
            status_metadata = {}

        return RepositoryFingerprint(
            repository_path=self.repository_path,
            fingerprint_hash=fingerprint_hash,
            total_files=total_files,
            total_classes=total_classes,
            total_functions=total_functions,
            total_lines=total_lines,
            languages=languages,
            artifacts=artifacts_set,
            dependency_graph=dependency_graph,
            risk_signals=risk_signals,
            status=fingerprint_status,
            status_metadata=status_metadata,
        )

    def _walk_repository(self) -> list[Path]:
        """Walk repository and return all processable files in deterministic order."""
        files: list[Path] = []

        for path in sorted(self.repository_path.rglob("*")):
            # Validate path remains within repository root (prevents symlink traversal)
            try:
                validated_path = self._validate_path_within_root(path)
            except FingerprintingError:
                logger.warning(f"Skipping path outside repository root: {path}")
                continue

            if validated_path.is_dir():
                if validated_path.name in self.IGNORE_DIRS:
                    continue
            elif validated_path.is_file():
                if validated_path.name in self.IGNORE_FILES:
                    continue
                if validated_path.suffix in self.SUPPORTED_EXTENSIONS:
                    files.append(validated_path)

        return sorted(files)

    def _process_file(self, file_path: Path) -> tuple[list[CodeArtifact], bool]:
        """Process a single file and extract artifacts.

        Returns:
            Tuple of (artifacts list, had_syntax_error bool)
        """
        artifacts: list[CodeArtifact] = []
        relative_path = file_path.relative_to(self.repository_path)
        had_syntax_error = False

        if file_path.suffix == ".py":
            try:
                content = file_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                line_count = len(lines)
                byte_size = file_path.stat().st_size

                file_artifact = FileArtifact(
                    artifact_type=CodeArtifactType.FILE,
                    name=relative_path.as_posix(),
                    path=relative_path,
                    start_line=1,
                    end_line=line_count,
                    language="python",
                    line_count=line_count,
                    byte_size=byte_size,
                )

                try:
                    tree = ast.parse(content, filename=str(file_path))
                    visitor = PythonASTVisitor(relative_path)
                    visitor.visit(tree)

                    if visitor.risk_signals:
                        file_artifact = FileArtifact(
                            artifact_type=CodeArtifactType.FILE,
                            name=relative_path.as_posix(),
                            path=relative_path,
                            start_line=1,
                            end_line=line_count,
                            language="python",
                            line_count=line_count,
                            byte_size=byte_size,
                            risk_signals=frozenset(visitor.risk_signals),
                        )

                    artifacts.append(file_artifact)
                    artifacts.extend(visitor.classes)
                    artifacts.extend(visitor.functions)
                except SyntaxError as e:
                    logger.warning(f"Syntax error in {file_path}: {e}")
                    artifacts.append(file_artifact)
                    had_syntax_error = True
            except UnicodeDecodeError:
                logger.warning(f"Cannot decode file {file_path} as UTF-8")
                had_syntax_error = True

        return artifacts, had_syntax_error

    def _build_dependency_graph(self, artifacts: list[CodeArtifact]) -> DependencyGraph:
        """Build dependency graph representing cross-file relationships."""
        edges: dict[str, set[str]] = {}

        file_artifacts = [a for a in artifacts if isinstance(a, FileArtifact)]
        class_artifacts = [a for a in artifacts if isinstance(a, ClassArtifact)]
        function_artifacts = [a for a in artifacts if isinstance(a, FunctionArtifact)]

        artifact_by_id: dict[str, CodeArtifact] = {}
        for artifact in artifacts:
            artifact_id = self._get_artifact_id(artifact)
            artifact_by_id[artifact_id] = artifact

        for class_artifact in class_artifacts:
            class_id = self._get_artifact_id(class_artifact)
            file_id = self._get_file_id_for_artifact(class_artifact, file_artifacts)
            if file_id:
                if class_id not in edges:
                    edges[class_id] = set()
                edges[class_id].add(file_id)

            for base_class in class_artifact.base_classes:
                base_id = self._find_class_id(base_class, class_artifacts, class_artifact.path)
                if base_id:
                    if class_id not in edges:
                        edges[class_id] = set()
                    edges[class_id].add(base_id)

        for func_artifact in function_artifacts:
            func_id = self._get_artifact_id(func_artifact)
            file_id = self._get_file_id_for_artifact(func_artifact, file_artifacts)
            if file_id:
                if func_id not in edges:
                    edges[func_id] = set()
                edges[func_id].add(file_id)

            class_name = func_artifact.metadata.get("class")
            if class_name and isinstance(class_name, str):
                func_class_id = self._find_class_id(class_name, class_artifacts, func_artifact.path)
                if func_class_id:
                    if func_id not in edges:
                        edges[func_id] = set()
                    edges[func_id].add(func_class_id)

        normalized_edges: dict[str, frozenset[str]] = {
            source: frozenset(targets) for source, targets in sorted(edges.items())
        }

        return DependencyGraph(edges=normalized_edges)

    def _get_file_id_for_artifact(
        self, artifact: CodeArtifact, file_artifacts: list[FileArtifact]
    ) -> str | None:
        """Find the file artifact ID that contains this artifact."""
        for file_artifact in file_artifacts:
            if file_artifact.path == artifact.path:
                return self._get_artifact_id(file_artifact)
        return None

    def _find_class_id(
        self, class_name: str, class_artifacts: list[ClassArtifact], file_path: Path
    ) -> str | None:
        """Find class artifact ID by name in the same file."""
        for class_artifact in class_artifacts:
            if class_artifact.name == class_name and class_artifact.path == file_path:
                return self._get_artifact_id(class_artifact)
        return None

    def _get_artifact_id(self, artifact: CodeArtifact) -> str:
        """Generate deterministic ID for an artifact."""
        return f"{artifact.path.as_posix()}:{artifact.artifact_type.value}:{artifact.name}:{artifact.start_line}"

    def _compute_fingerprint_hash(
        self, artifacts: list[CodeArtifact], graph: DependencyGraph
    ) -> str:
        """Compute deterministic hash of fingerprint."""
        hash_input: list[str] = []

        for artifact in sorted(artifacts, key=lambda a: (a.path.as_posix(), a.start_line, a.name)):
            artifact_repr = f"{artifact.artifact_type.value}:{artifact.path.as_posix()}:{artifact.name}:{artifact.start_line}:{artifact.end_line}"
            if artifact.risk_signals:
                signals_str = ",".join(sorted(s.value for s in artifact.risk_signals))
                artifact_repr += f":{signals_str}"
            hash_input.append(artifact_repr)

        for source in sorted(graph.edges.keys()):
            for target in sorted(graph.edges[source]):
                hash_input.append(f"{source}->{target}")

        hash_str = "\n".join(hash_input)
        return hashlib.sha256(hash_str.encode("utf-8")).hexdigest()
