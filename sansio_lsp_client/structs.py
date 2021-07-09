import enum
import typing as t
from typing_extensions import Literal

from pydantic import BaseModel, Field

# XXX: Replace the non-commented-out code with what's commented out once nested
# types become a thing in mypy.
# JSONValue = t.Union[None, str, int,
#                     t.List['JSONValue'], t.Dict[str, 'JSONValue']]
# JSONDict = t.Dict[str, JSONValue]
JSONDict = t.Dict[str, t.Any]

Id = t.Union[int, str]

ProgressToken = t.Union[int, str]


class Request(BaseModel):
    method: str
    id: t.Optional[Id]
    params: t.Optional[JSONDict]


class Response(BaseModel):
    id: t.Optional[Id]
    result: t.Optional[t.Union[t.List[t.Any], JSONDict]]
    error: t.Optional[JSONDict]


class MessageType(enum.IntEnum):
    ERROR = 1
    WARNING = 2
    INFO = 3
    LOG = 4


class MessageActionItem(BaseModel):
    title: str


class TextDocumentItem(BaseModel):
    uri: str
    languageId: str
    version: int
    text: str


class TextDocumentIdentifier(BaseModel):
    uri: str


class VersionedTextDocumentIdentifier(TextDocumentIdentifier):
    version: t.Optional[int]


# Sorting tip:  sorted(positions, key=(lambda p: p.as_tuple()))
class Position(BaseModel):
    # NB: These are both zero-based.
    line: int
    character: int

    def as_tuple(self) -> t.Tuple[int, int]:
        return (self.line, self.character)


class Range(BaseModel):
    start: Position
    end: Position

    def calculate_length(self, text: str) -> int:
        text_lines = text.splitlines()

        if self.end.line == self.start.line:
            line = text_lines[self.start.line]
            return len(line[self.start.character : self.end.character])
        else:
            total = 0

            total += len(text_lines[self.start.line][self.start.character :])

            for line_number in range(self.start.line + 1, self.end.line):
                total += len(text_lines[line_number])

            total += len(text_lines[self.end.line][: self.end.character])

            return total


class TextDocumentContentChangeEvent(BaseModel):
    text: str
    range: t.Optional[Range]
    rangeLength: t.Optional[int]  # deprecated, use .range

    def dict(self, **kwargs: t.Any) -> t.Dict[str, t.Any]:
        d = super().dict(**kwargs)

        # vscode-css server requires un-filled values to be absent
        # TODO: add vscode-css to tests
        if self.rangeLength is None:
            del d["rangeLength"]
        if self.range is None:
            del d["range"]
        return d

    @classmethod
    def range_change(
        cls,
        change_start: Position,
        change_end: Position,
        change_text: str,
        old_text: str,
    ) -> "TextDocumentContentChangeEvent":
        """
        Create a TextDocumentContentChangeEvent reflecting the given changes.

        Nota bene: If you're creating a list of
        TextDocumentContentChangeEvent based on many changes, `old_text` must
        reflect the state of the text after all previous change events
        happened.
        """
        change_range = Range(start=change_start, end=change_end)
        return cls(
            range=change_range,
            rangeLength=change_range.calculate_length(old_text),
            text=change_text,
        )

    @classmethod
    def whole_document_change(
        cls, change_text: str
    ) -> "TextDocumentContentChangeEvent":
        return cls(text=change_text)


class TextDocumentPosition(BaseModel):
    textDocument: TextDocumentIdentifier
    position: Position


class CompletionTriggerKind(enum.IntEnum):
    INVOKED = 1
    TRIGGER_CHARACTER = 2
    TRIGGER_FOR_INCOMPLETE_COMPLETIONS = 3


class CompletionContext(BaseModel):
    triggerKind: CompletionTriggerKind
    triggerCharacter: t.Optional[str]


class MarkupKind(enum.Enum):
    PLAINTEXT = "plaintext"
    MARKDOWN = "markdown"


class MarkupContent(BaseModel):
    kind: MarkupKind
    value: str


class TextEdit(BaseModel):
    range: Range
    newText: str


class Command(BaseModel):
    title: str
    command: str
    arguments: t.Optional[t.List[t.Any]]


class InsertTextFormat(enum.IntEnum):
    PLAIN_TEXT = 1
    SNIPPET = 2


class CompletionItemKind(enum.IntEnum):
    TEXT = 1
    METHOD = 2
    FUNCTION = 3
    CONSTRUCTOR = 4
    FIELD = 5
    VARIABLE = 6
    CLASS = 7
    INTERFACE = 8
    MODULE = 9
    PROPERTY = 10
    UNIT = 11
    VALUE = 12
    ENUM = 13
    KEYWORD = 14
    SNIPPET = 15
    COLOR = 16
    FILE = 17
    REFERENCE = 18
    FOLDER = 19
    ENUMMEMBER = 20
    CONSTANT = 21
    STRUCT = 22
    EVENT = 23
    OPERATOR = 24
    TYPEPARAMETER = 25


class CompletionItemTag(enum.IntEnum):
    DEPRECATED = 1


class CompletionItem(BaseModel):
    label: str
    kind: t.Optional[CompletionItemKind]
    tags: t.Optional[CompletionItemTag]
    detail: t.Optional[str]
    documentation: t.Union[str, MarkupContent, None]
    deprecated: t.Optional[bool]
    preselect: t.Optional[bool]
    sortText: t.Optional[str]
    filterText: t.Optional[str]
    insertText: t.Optional[str]
    insertTextFormat: t.Optional[InsertTextFormat]
    textEdit: t.Optional[TextEdit]
    additionalTextEdits: t.Optional[t.List[TextEdit]]
    commitCharacters: t.Optional[t.List[str]]
    command: t.Optional[Command]
    data: t.Optional[t.Any]


class CompletionList(BaseModel):
    isIncomplete: bool
    items: t.List[CompletionItem]


class TextDocumentSaveReason(enum.IntEnum):
    MANUAL = 1
    AFTER_DELAY = 2
    FOCUS_OUT = 3


class Location(BaseModel):
    uri: str
    range: Range


class LocationLink(BaseModel):
    originSelectionRange: t.Optional[Range]
    targetUri: str  # in the spec the type is DocumentUri
    targetRange: Range
    targetSelectionRange: Range


class DiagnosticRelatedInformation(BaseModel):
    location: Location
    message: str


class DiagnosticSeverity(enum.IntEnum):
    ERROR = 1
    WARNING = 2
    INFORMATION = 3
    HINT = 4


class Diagnostic(BaseModel):
    range: Range

    severity: t.Optional[DiagnosticSeverity]

    code: t.Optional[t.Union[int, str]]

    source: t.Optional[str]

    message: str

    relatedInformation: t.Optional[t.List[DiagnosticRelatedInformation]]


class MarkedString(BaseModel):
    language: str
    value: str


class ParameterInformation(BaseModel):
    label: t.Union[str, t.Tuple[int, int]]
    documentation: t.Optional[t.Union[str, MarkupContent]]


class SignatureInformation(BaseModel):
    label: str
    documentation: t.Optional[t.Union[MarkupContent, str]]
    parameters: t.Optional[t.List[ParameterInformation]]
    activeParameter: t.Optional[int]


class SymbolKind(enum.IntEnum):
    FILE = 1
    MODULE = 2
    NAMESPACE = 3
    PACKAGE = 4
    CLASS = 5
    METHOD = 6
    PROPERTY = 7
    FIELD = 8
    CONSTRUCTOR = 9
    ENUM = 10
    INTERFACE = 11
    FUNCTION = 12
    VARIABLE = 13
    CONSTANT = 14
    STRING = 15
    NUMBER = 16
    bool = 17
    ARRAY = 18
    OBJECT = 19
    KEY = 20
    NULL = 21
    ENUMMEMBER = 22
    STRUCT = 23
    EVENT = 24
    OPERATOR = 25
    TYPEPARAMETER = 26


class SymbolTag(enum.IntEnum):
    DEPRECATED = 1


class CallHierarchyItem(BaseModel):
    name: str
    king: SymbolKind
    tags: t.Optional[SymbolTag]
    detail: t.Optional[str]
    uri: str
    range: Range
    selectionRange: Range
    data: t.Optional[t.Any]


class CallHierarchyIncomingCall(BaseModel):
    from_: CallHierarchyItem
    fromRanges: t.List[Range]

    class Config:
        # 'from' is an invalid field - re-mapping
        fields = {"from_": "from"}


class CallHierarchyOutgoingCall(BaseModel):
    to: CallHierarchyItem
    fromRanges: t.List[Range]


class TextDocumentSyncKind(enum.IntEnum):
    NONE = 0
    FULL = 1
    INCREMENTAL = 2


# Usually in a flat list
class SymbolInformation(BaseModel):
    name: str
    kind: SymbolKind
    tags: t.Optional[t.List[SymbolTag]]
    deprecated: t.Optional[bool]
    location: Location
    containerName: t.Optional[str]


# Usually a hierarchy, e.g. a symbol with kind=SymbolKind.CLASS contains
# several SymbolKind.METHOD symbols
class DocumentSymbol(BaseModel):
    name: str
    detail: t.Optional[str]
    kind: SymbolKind
    tags: t.Optional[t.List[SymbolTag]]
    deprecated: t.Optional[bool]
    range: Range
    selectionRange: Range  # Example: symbol.selectionRange.start.as_tuple()
    # https://stackoverflow.com/questions/36193540
    children: t.Optional[t.List["DocumentSymbol"]]


# for `.children` treeness
DocumentSymbol.update_forward_refs()


class Registration(BaseModel):
    id: str
    method: str
    registerOptions: t.Optional[t.Any]


class FormattingOptions(BaseModel):
    tabSize: int
    insertSpaces: bool
    trimTrailingWhitespace: t.Optional[bool]
    insertFinalNewline: t.Optional[bool]
    trimFinalNewlines: t.Optional[bool]


class WorkspaceFolder(BaseModel):
    uri: str
    name: str


class ProgressValue(BaseModel):
    pass


class WorkDoneProgressValue(ProgressValue):
    pass


class MWorkDoneProgressKind(enum.Enum):
    BEGIN = "begin"
    REPORT = "report"
    END = "end"


class WorkDoneProgressBeginValue(WorkDoneProgressValue):
    kind: Literal["begin"]
    title: str
    cancellable: t.Optional[bool]
    message: t.Optional[str]
    percentage: t.Optional[int]


class WorkDoneProgressReportValue(WorkDoneProgressValue):
    kind: Literal["report"]
    cancellable: t.Optional[bool]
    message: t.Optional[str]
    percentage: t.Optional[int]


class WorkDoneProgressEndValue(WorkDoneProgressValue):
    kind: Literal["end"]
    message: t.Optional[str]


class ConfigurationItem(BaseModel):
    scopeUri: t.Optional[str]
    section: t.Optional[str]


class WorkspaceFileOperations(BaseModel):
    dynamicRegistration: t.Optional[bool]
    didCreate: t.Optional[bool]
    willCreate: t.Optional[bool]
    didRename: t.Optional[bool]
    willRename: t.Optional[bool]
    didDelete: t.Optional[bool]
    willDelete: t.Optional[bool]


class WorkspaceEditClientChangeAnnotationSupport(BaseModel):
    groupsOnLabel: t.Optional[bool]


class FailureHandlingKind(enum.Enum):
    Abort = "abort"
    Transactional = "transactional"
    TextOnlyTransactional = "textOnlyTransactional"
    Undo = "undo"


class ResourceOperationKind(enum.Enum):
    Create = "create"
    Rename = "rename"
    Delete = "delete"


class WorkspaceEditClientCapabilities(BaseModel):
    documentChanges: t.Optional[bool]
    resourceOperations: t.Optional[t.List[ResourceOperationKind]]
    failureHandling: t.Optional[FailureHandlingKind]
    normalizesLineEndings: t.Optional[bool]
    changeAnnotationSupport: t.Optional[WorkspaceEditClientChangeAnnotationSupport]


class DidChangeConfigurationClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class DidChangeWatchedFilesClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class WorkspaceSymbolKindCapabilities(BaseModel):
    valueSet: t.Optional[t.List[SymbolKind]]


class WorkspaceTagSupportCapabilities(BaseModel):
    valueSet: t.List[SymbolTag]


class WorkspaceSymbolClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    symbolKind: t.Optional[WorkspaceSymbolKindCapabilities]
    tagSupport: t.Optional[WorkspaceTagSupportCapabilities]


class ExecuteCommandClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class SemanticTokensWorkspaceClientCapabilities(BaseModel):
    refreshSupport: t.Optional[bool]


class CodeLensWorkspaceClientCapabilities(BaseModel):
    refreshSupport: t.Optional[bool]


class ShowMessageRequestActionItem(BaseModel):
    additionalPropertiesSupport: t.Optional[bool]


class ShowMessageRequestClientCapabilities(BaseModel):
    messageActionItem: t.Optional[ShowMessageRequestActionItem]


class ClientWorkspaceCapabilities(BaseModel):
    applyEdit: t.Optional[bool]
    workspaceEdit: t.Optional[WorkspaceEditClientCapabilities]
    didChangeConfiguration: t.Optional[DidChangeConfigurationClientCapabilities]
    didChangeWatchedFiles: t.Optional[DidChangeWatchedFilesClientCapabilities]
    symbol: t.Optional[WorkspaceSymbolClientCapabilities]
    executeCommand: t.Optional[ExecuteCommandClientCapabilities]
    workspaceFolders: bool
    configuration: bool
    semanticTokens: t.Optional[SemanticTokensWorkspaceClientCapabilities]
    codeLens: t.Optional[CodeLensWorkspaceClientCapabilities]
    fileOperations: t.Optional[WorkspaceFileOperations]


class ShowDocumentClientCapabilities(BaseModel):
    support: bool


class RegularExpressionsClientCapabilities(BaseModel):
    engine: str
    version: t.Optional[str]


class ClientWindowCapabilities(BaseModel):
    workDoneProgress: t.Optional[bool]
    showMessage: t.Optional[ShowMessageRequestClientCapabilities]
    showDocument: t.Optional[ShowDocumentClientCapabilities]


class MarkdownClientCapabilities(BaseModel):
    parser: str
    version: t.Optional[str]


class ClientGeneralCapabilities(BaseModel):
    regularExpressions: t.Optional[RegularExpressionsClientCapabilities]
    markdown: t.Optional[MarkdownClientCapabilities]


class TextDocumentSyncClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    willSave: t.Optional[bool]
    willSaveWaitUntil: t.Optional[bool]
    didSave: t.Optional[bool]


class CompletionClientCapabilityItemTagSupport(BaseModel):
    valueSet: t.List[CompletionItemTag]


class CompletionClientCapabilityItemResolveSupport(BaseModel):
    properties: t.List[str]


class InsertTextMode(enum.IntEnum):
    asIs = 1
    adjustIndentation = 2


class CompletionClientCapabilityItemInsertTextModeSupport(BaseModel):
    valueSet: t.List[InsertTextMode]


class CompletionClientCapabilityItem(BaseModel):
    snippetSupport: t.Optional[bool]
    commitCharactersSupport: t.Optional[bool]
    documentationFormat: t.Optional[t.List[MarkupKind]]
    deprecatedSupport: t.Optional[bool]
    preselectSupport: t.Optional[bool]
    tagSupport: t.Optional[CompletionClientCapabilityItemTagSupport]
    insertReplaceSupport: t.Optional[bool]
    resolveSupport: t.Optional[CompletionClientCapabilityItemResolveSupport]
    insertTextModeSupport: t.Optional[
        CompletionClientCapabilityItemInsertTextModeSupport
    ]
    labelDetailsSupport: t.Optional[bool]


class CompletionClientCapabilityItemKind(BaseModel):
    valueSet: t.Optional[t.List[CompletionItemKind]]


class CompletionClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    completionItem: t.Optional[CompletionClientCapabilityItem]
    completionItemKind: t.Optional[CompletionClientCapabilityItemKind]
    contextSupport: t.Optional[bool]
    insertTextMode: t.Optional[InsertTextMode]


class HoverClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    contentFormat: t.Optional[t.List[MarkupKind]]


class SignatureHelpClientCapabilityParameterInformation(BaseModel):
    labelOffsetSupport: t.Optional[bool]


class SignatureHelpClientCapabilityInformation(BaseModel):
    documentationFormat: t.Optional[t.List[MarkupKind]]
    parameterInformation: t.Optional[SignatureHelpClientCapabilityParameterInformation]
    activeParameterSupport: t.Optional[bool]


class SignatureHelpClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    signatureInformation: t.Optional[SignatureHelpClientCapabilityInformation]
    contextSupport: t.Optional[bool]


class DeclarationClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    linkSupport: t.Optional[bool]


class DefinitionClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    linkSupport: t.Optional[bool]


class TypeDefinitionClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    linkSupport: t.Optional[bool]


class ImplementationClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    linkSupport: t.Optional[bool]


class ReferenceClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class DocumentHighlightClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class DocumentSymbolClientCapabilitySymbolKind(BaseModel):
    valueSet: t.Optional[t.List[SymbolKind]]


class DocumentSymbolClientCapabilityTagSupport(BaseModel):
    valueSet: t.List[SymbolTag]


class DocumentSymbolClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    symbolKind: t.Optional[DocumentSymbolClientCapabilitySymbolKind]
    hierarchicalDocumentSymbolSupport: t.Optional[bool]
    tagSupport: t.Optional[DocumentSymbolClientCapabilityTagSupport]
    labelSupport: t.Optional[bool]


class CodeActionKind(enum.Enum):
    Empty = ""
    QuickFix = "quickfix"
    Refactor = "refactor"
    RefactorExtract = "refactor.extract"
    RefactorInline = "refactor.inline"
    RefactorRewrite = "refactor.rewrite"
    Source = "source"
    SourceOrganizeImports = "source.organizeImports"
    SourceFixAll = "source.fixAll"


class CodeActionClientCapabilityLiteralSupportKind(BaseModel):
    valueSet: t.List[CodeActionKind]


class CodeActionClientCapabilityLiteralSupport(BaseModel):
    codeActionKind: CodeActionClientCapabilityLiteralSupportKind


class CodeActionClientCapabilityResolveSupport(BaseModel):
    properties: t.List[str]


class CodeActionClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    codeActionLiteralSupport: t.Optional[CodeActionClientCapabilityLiteralSupport]
    isPreferredSupport: t.Optional[bool]
    disabledSupport: t.Optional[bool]
    dataSupport: t.Optional[bool]
    resolveSupport: t.Optional[CodeActionClientCapabilityResolveSupport]
    honorsChangeAnnotations: t.Optional[bool]


class CodeLensClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class DocumentLinkClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    tooltipSupport: t.Optional[bool]


class DocumentColorClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class DocumentFormattingClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class DocumentRangeFormattingClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class DocumentOnTypeFormattingClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class PrepareSupportDefaultBehavior(enum.IntEnum):
    Identifier = 1


class RenameClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    prepareSupport: t.Optional[bool]
    prepareSupportDefaultBehavior: t.Optional[PrepareSupportDefaultBehavior]
    honorsChangeAnnotations: t.Optional[bool]


class DiagnosticTag(enum.IntEnum):
    Unnecessary = 1
    Deprecated = 2


class PublishDiagnosticsClientCapabilityTagSupport(BaseModel):
    valueSet: t.List[DiagnosticTag]


class PublishDiagnosticsClientCapabilities(BaseModel):
    relatedInformation: t.Optional[bool]
    tagSupport: t.Optional[PublishDiagnosticsClientCapabilityTagSupport]
    versionSupport: t.Optional[bool]
    codeDescriptionSupport: t.Optional[bool]
    dataSupport: t.Optional[bool]


class FoldingRangeClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    rangeLimit: t.Optional[int] = Field(None, ge=0)
    lineFoldingOnly: t.Optional[bool]


class SelectionRangeClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class LinkedEditingRangeClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class CallHierarchyClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class SemanticTokensClientCapabilityRequestsRange(BaseModel):
    pass


class SemanticTokensClientCapabilityRequestsFull(BaseModel):
    delta: t.Optional[bool]


class SemanticTokensClientCapabilityRequests(BaseModel):
    range: t.Optional[t.Union[bool, SemanticTokensClientCapabilityRequestsRange]]
    full: t.Optional[t.Union[bool, SemanticTokensClientCapabilityRequestsFull]]


class TokenFormat(enum.Enum):
    Relative = "relative"


class SemanticTokensClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]
    requests: SemanticTokensClientCapabilityRequests
    tokenTypes: t.List[str]
    tokenModifiers: t.List[str]
    formats: t.List[TokenFormat]
    overlappingTokenSupport: t.Optional[bool]
    multilineTokenSupport: t.Optional[bool]


class MonikerClientCapabilities(BaseModel):
    dynamicRegistration: t.Optional[bool]


class TextDocumentClientCapabilities(BaseModel):
    synchronization: t.Optional[TextDocumentSyncClientCapabilities]
    completion: t.Optional[CompletionClientCapabilities]
    hover: t.Optional[HoverClientCapabilities]
    signatureHelp: t.Optional[SignatureHelpClientCapabilities]
    declaration: t.Optional[DeclarationClientCapabilities]
    definition: t.Optional[DefinitionClientCapabilities]
    typeDefinition: t.Optional[TypeDefinitionClientCapabilities]
    implementation: t.Optional[ImplementationClientCapabilities]
    references: t.Optional[ReferenceClientCapabilities]
    documentHighlight: t.Optional[DocumentHighlightClientCapabilities]
    documentSymbol: t.Optional[DocumentSymbolClientCapabilities]
    codeAction: t.Optional[CodeActionClientCapabilities]
    codeLens: t.Optional[CodeLensClientCapabilities]
    documentLink: t.Optional[DocumentLinkClientCapabilities]
    colorProvider: t.Optional[DocumentColorClientCapabilities]
    formatting: t.Optional[DocumentFormattingClientCapabilities]
    rangeFormatting: t.Optional[DocumentRangeFormattingClientCapabilities]
    onTypeFormatting: t.Optional[DocumentOnTypeFormattingClientCapabilities]
    rename: t.Optional[RenameClientCapabilities]
    publishDiagnostics: t.Optional[PublishDiagnosticsClientCapabilities]
    foldingRange: t.Optional[FoldingRangeClientCapabilities]
    selectionRange: t.Optional[SelectionRangeClientCapabilities]
    linkedEditingRange: t.Optional[LinkedEditingRangeClientCapabilities]
    callHierarchy: t.Optional[CallHierarchyClientCapabilities]
    semanticTokens: t.Optional[SemanticTokensClientCapabilities]
    moniker: t.Optional[MonikerClientCapabilities]


class ClientCapabilities(BaseModel):
    workspace: t.Optional[ClientWorkspaceCapabilities]
    textDocument: t.Optional[TextDocumentClientCapabilities]
    window: t.Optional[ClientWindowCapabilities]
    general: t.Optional[ClientGeneralCapabilities]
    experimental: t.Optional[t.Any]


class FileOperationPatternKind(enum.Enum):
    file = "file"
    folder = "folder"


class FileOperationPatternOptions(BaseModel):
    ignoreCase: t.Optional[bool]


class FileOperationPattern(BaseModel):
    glob: str
    matches: t.Optional[FileOperationPatternKind]
    options: t.Optional[FileOperationPatternOptions]


class FileOperationFilter(BaseModel):
    scheme: t.Optional[str]
    pattern: FileOperationPattern


class FileOperationRegistrationOptions(BaseModel):
    filters: t.List[FileOperationFilter]


class ServerCapabilityWorkspaceFileOperations(BaseModel):
    didCreate: t.Optional[FileOperationRegistrationOptions]
    willCreate: t.Optional[FileOperationRegistrationOptions]
    didRename: t.Optional[FileOperationRegistrationOptions]
    willRename: t.Optional[FileOperationRegistrationOptions]
    didDelete: t.Optional[FileOperationRegistrationOptions]
    willDelete: t.Optional[FileOperationRegistrationOptions]


class WorkspaceFoldersServerCapabilities(BaseModel):
    supported: t.Optional[bool]
    changeNotifications: t.Optional[t.Union[str, bool]]


class ServerCapabilityWorkspace(BaseModel):
    workspaceFolders: t.Optional[WorkspaceFoldersServerCapabilities]
    fileOperations: t.Optional[ServerCapabilityWorkspaceFileOperations]


class TextDocumentSyncOptions(BaseModel):
    openClose: t.Optional[bool]
    change: t.Optional[TextDocumentSyncKind]


class WorkDoneProgressOptions(BaseModel):
    workDoneProgress: t.Optional[bool]


class CompletionOptionItem(WorkDoneProgressOptions):
    labelDetailsSupport: t.Optional[bool]


class CompletionOptions(WorkDoneProgressOptions):
    triggerCharacters: t.Optional[t.List[str]]
    allCommitCharacters: t.Optional[t.List[str]]
    resolveProvider: t.Optional[bool]
    completionItem: t.Optional[CompletionOptionItem]


class HoverOptions(WorkDoneProgressOptions):
    pass


class SignatureHelpOptions(WorkDoneProgressOptions):
    triggerCharacters: t.Optional[t.List[str]]
    retriggerCharacters: t.Optional[t.List[str]]


class DeclarationOptions(WorkDoneProgressOptions):
    pass


class DocumentFilter(BaseModel):
    language: t.Optional[str]
    scheme: t.Optional[str]
    pattern: t.Optional[str]


DocumentSelector = t.List[DocumentFilter]


class TextDocumentRegistrationOptions(BaseModel):
    documentSelector: t.Union[DocumentSelector, None]


class StaticRegistrationOptions(BaseModel):
    id: t.Optional[str]


class DeclarationRegistrationOptions(
    DeclarationOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions
):
    pass


class DefinitionOptions(WorkDoneProgressOptions):
    pass


class TypeDefinitionOptions(WorkDoneProgressOptions):
    pass


class TypeDefinitionRegistrationOptions(
    TextDocumentRegistrationOptions, TypeDefinitionOptions, StaticRegistrationOptions
):
    pass


class ImplementationOptions(WorkDoneProgressOptions):
    pass


class ImplementationRegistrationOptions(
    TextDocumentRegistrationOptions, ImplementationOptions, StaticRegistrationOptions
):
    pass


class ReferenceOptions(WorkDoneProgressOptions):
    pass


class DocumentHighlightOptions(WorkDoneProgressOptions):
    pass


class DocumentSymbolOptions(WorkDoneProgressOptions):
    label: t.Optional[str]


class CodeActionOptions(WorkDoneProgressOptions):
    codeActionKinds: t.Optional[t.List[CodeActionKind]]
    resolveProvider: t.Optional[bool]


class CodeLensOptions(WorkDoneProgressOptions):
    resolveProvider: t.Optional[bool]


class DocumentLinkOptions(WorkDoneProgressOptions):
    resolveProvider: t.Optional[bool]


class DocumentColorOptions(WorkDoneProgressOptions):
    pass


class DocumentColorRegistrationOptions(
    TextDocumentRegistrationOptions, StaticRegistrationOptions, DocumentColorOptions
):
    pass


class DocumentFormattingOptions(WorkDoneProgressOptions):
    pass


class DocumentRangeFormattingOptions(WorkDoneProgressOptions):
    pass


class DocumentOnTypeFormattingOptions(BaseModel):
    firstTriggerCharacter: str
    moreTriggerCharacter: t.Optional[t.List[str]]


class RenameOptions(WorkDoneProgressOptions):
    prepareProvider: t.Optional[bool]


class FoldingRangeOptions(WorkDoneProgressOptions):
    pass


class FoldingRangeRegistrationOptions(
    TextDocumentRegistrationOptions, FoldingRangeOptions, StaticRegistrationOptions
):
    pass


class ExecuteCommandOptions(WorkDoneProgressOptions):
    commands: t.List[str]


class SelectionRangeOptions(WorkDoneProgressOptions):
    pass


class SelectionRangeRegistrationOptions(
    SelectionRangeOptions, TextDocumentRegistrationOptions, StaticRegistrationOptions
):
    pass


class LinkedEditingRangeOptions(WorkDoneProgressOptions):
    pass


class LinkedEditingRangeRegistrationOptions(
    TextDocumentRegistrationOptions,
    LinkedEditingRangeOptions,
    StaticRegistrationOptions,
):
    pass


class CallHierarchyOptions(WorkDoneProgressOptions):
    pass


class CallHierarchyRegistrationOptions(
    TextDocumentRegistrationOptions, CallHierarchyOptions, StaticRegistrationOptions
):
    pass


class SemanticTokensLegend(BaseModel):
    tokenTypes: t.List[str]
    tokenModifiers: t.List[str]


class SemanticTokensOptions(WorkDoneProgressOptions):
    legend: SemanticTokensLegend
    range: t.Optional[t.Union[bool, SemanticTokensClientCapabilityRequestsRange]]
    full: t.Optional[t.Union[bool, SemanticTokensClientCapabilityRequestsFull]]


class SemanticTokensRegistrationOptions(
    TextDocumentRegistrationOptions, SemanticTokensOptions, StaticRegistrationOptions
):
    pass


class MonikerOptions(WorkDoneProgressOptions):
    pass


class MonikerRegistrationOptions(TextDocumentRegistrationOptions, MonikerOptions):
    pass


class WorkspaceSymbolOptions(WorkDoneProgressOptions):
    pass


class ServerCapabilities(BaseModel):
    textDocumentSync: t.Optional[t.Union[TextDocumentSyncOptions, TextDocumentSyncKind]]
    completionProvider: t.Optional[CompletionOptions]
    hoverProvider: t.Optional[t.Union[bool, HoverOptions]]
    signatureHelpProvider: t.Optional[SignatureHelpOptions]
    declarationProvider: t.Optional[
        t.Union[bool, DeclarationOptions, DeclarationRegistrationOptions]
    ]
    definitionProvider: t.Optional[t.Union[bool, DefinitionOptions]]
    typeDefinitionProvider: t.Optional[
        t.Union[bool, TypeDefinitionOptions, TypeDefinitionRegistrationOptions]
    ]
    implementationProvider: t.Optional[
        t.Union[bool, ImplementationOptions, ImplementationRegistrationOptions]
    ]
    referencesProvider: t.Optional[t.Union[bool, ReferenceOptions]]
    documentHighlightProvider: t.Optional[t.Union[bool, DocumentHighlightOptions]]
    documentSymbolProvider: t.Optional[t.Union[bool, DocumentSymbolOptions]]
    codeActionProvider: t.Optional[t.Union[bool, CodeActionOptions]]
    codeLensProvider: t.Optional[CodeLensOptions]
    documentLinkProvider: t.Optional[DocumentLinkOptions]
    colorProvider: t.Optional[
        t.Union[bool, DocumentColorOptions, DocumentColorRegistrationOptions]
    ]
    documentFormattingProvider: t.Optional[t.Union[bool, DocumentFormattingOptions]]
    documentRangeFormattingProvider: t.Optional[
        t.Union[bool, DocumentRangeFormattingOptions]
    ]
    documentOnTypeFormattingProvider: t.Optional[DocumentOnTypeFormattingOptions]
    renameProvider: t.Optional[t.Union[bool, RenameOptions]]
    foldingRangeProvider: t.Optional[
        t.Union[bool, FoldingRangeOptions, FoldingRangeRegistrationOptions]
    ]
    executeCommandProvider: t.Optional[ExecuteCommandOptions]
    selectionRangeProvider: t.Optional[
        t.Union[bool, SelectionRangeOptions, SelectionRangeRegistrationOptions]
    ]
    linkedEditingRangeProvider: t.Optional[
        t.Union[bool, LinkedEditingRangeOptions, LinkedEditingRangeRegistrationOptions]
    ]
    callHierarchyProvider: t.Optional[
        t.Union[bool, CallHierarchyOptions, CallHierarchyRegistrationOptions]
    ]
    semanticTokensProvider: t.Optional[
        t.Union[SemanticTokensOptions, SemanticTokensRegistrationOptions]
    ]
    monikerProvider: t.Optional[
        t.Union[bool, MonikerOptions, MonikerRegistrationOptions]
    ]
    workspaceSymbolProvider: t.Optional[t.Union[bool, WorkspaceSymbolOptions]]
    workspace: t.Optional[ServerCapabilityWorkspace]
    experimental: t.Optional[t.Any]


class ServerInfo(BaseModel):
    name: str
    version: t.Optional[str]
