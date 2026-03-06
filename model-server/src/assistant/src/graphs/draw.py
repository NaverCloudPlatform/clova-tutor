# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import importlib
import inspect
import pkgutil
from collections import defaultdict
from types import FunctionType, ModuleType
from typing import Dict, Iterable, List, Tuple, get_args

import graphviz

from assistant.src.graphs import node


def iter_modules(pkg: ModuleType) -> Iterable[ModuleType]:
    """pkg 이하의 모든 모듈(패키지·서브패키지 포함)을 임포트해 yield."""
    yield pkg  # 루트 패키지도 포함
    prefix = pkg.__name__ + "."
    for _, mod_name, is_pkg in pkgutil.walk_packages(pkg.__path__, prefix):
        module = importlib.import_module(mod_name)
        yield module


def collect_functions(pkg: ModuleType) -> Dict[str, List[FunctionType]]:
    """
    패키지 내 모든 함수 객체를 모아
    { '모듈이름': [func1, func2, ...], ... } 형태로 반환.
    """
    funcs_by_module = defaultdict(list)

    for module in iter_modules(pkg):
        # 모듈 전역에서 함수 탐색
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            # 모듈이 동적으로 재할당한 타 모듈 함수까지 원한다면 아래 주석 해제
            # if obj.__module__ != module.__name__:
            #     continue
            funcs_by_module[module.__name__].append(obj)

    return funcs_by_module


def get_function_description(func: FunctionType) -> List[List[str]]:
    """
    conditional branch의 설명을 docstring에서 추출합니다.
    docstring이 없으면 빈 값을 반환합니다.
    """
    descriptions = []
    if func.__doc__:
        # docstring에서 "condition: node_name" 형태로 된 정보 추출
        doc_lines = func.__doc__.strip().split("\n")

        descriptions = []
        for line in doc_lines:
            if ":" in line:
                condition, node_name = line.split(":")
                condition, node_name = condition.strip(), node_name.strip()
                descriptions.append(
                    [func.__name__, node_name, condition]
                )  # start_node, end_node, condition

    # docstring이 없으면 빈 값 반환
    return descriptions


def collect_command_edges(func_list: List[FunctionType]) -> List[Tuple[str, str]]:
    edges = []
    for func in func_list:
        start = func.__name__
        end = func.__annotations__.get("return")
        if end and get_args(end):
            end = get_args(get_args(end)[0])

            for _end in end:
                edges.append((start, _end))
    return edges


def collect_edges(func_list: List[FunctionType]) -> List[Tuple[str, str]]:
    """함수 리스트에서 엣지 정보를 추출"""
    edges = collect_command_edges(func_list)
    return edges


def find_root_nodes(edges: List[Tuple[str, str]]) -> List[str]:
    """트리의 루트 노드들을 찾기 (들어오는 엣지가 없는 노드들)"""
    all_nodes = set()
    target_nodes = set()

    for start, end in edges:
        all_nodes.add(start)
        all_nodes.add(end)
        target_nodes.add(end)

    return list(all_nodes - target_nodes)


def draw_graph_with_graphviz(
    edges: List[Tuple[str, str]],
    condition_info: List[List[str]],
    output_path: str = "graph_graphviz",
    color_mapping: Dict[str, str] = {},
    **kwargs,
):
    # Digraph 생성
    dot = graphviz.Digraph(comment="Function Call Graph")
    dot.attr(rankdir="TB")  # Top to Bottom layout for tree structure
    # 노드 스타일 설정
    dot.attr(
        "node",
        shape="box",
        style="rounded,filled",
        fillcolor="lavender",
        fontname="Arial",
        fontsize=str(kwargs.get("node_font_size", "10")),
    )

    # 엣지 스타일 설정
    dot.attr(
        "edge",
        fontname="Arial",
        fontsize=str(kwargs.get("edge_font_size", "10")),
        fontcolor="gray16",
        color="black",
        penwidth="0.8",
    )

    # 모든 노드 추가
    all_nodes = set()
    for start, end in edges:
        all_nodes.add(start)
        all_nodes.add(end)

    for node_name in all_nodes:
        dot.node(
            node_name, node_name, fillcolor=color_mapping.get(node_name, "lavender")
        )

    # 조건 정보를 딕셔너리로 변환 (start_node -> end_node -> condition)
    condition_dict = {}
    for start_node, end_node, condition in condition_info:
        if start_node not in condition_dict:
            condition_dict[start_node] = {}
        condition_dict[start_node][end_node] = condition

    # 엣지 추가 (조건 라벨 포함)
    for start, end in edges:
        # 해당 엣지의 조건 라벨 찾기
        edge_label = ""
        if start in condition_dict and end in condition_dict[start]:
            edge_label = condition_dict[start][end]

        dot.edge(start, end, label=edge_label)

    # 파일로 저장
    dot.render(output_path, format="png", cleanup=True)
    print(f"Graphviz graph saved to {output_path}.png")


def get_color_mapping(
    funcs: Dict[str, List[FunctionType]], edges: List[Tuple[str, str]]
) -> Dict[str, str]:

    # color mapping 정의
    node_color_palette = ["lavender", "khaki", "honeydew", "lightblue", "moccasin"]
    color_mapping = {}
    i = 0
    for module, func_list in funcs.items():
        for func in func_list:
            if func.__module__ == module:
                color_mapping[func.__name__] = node_color_palette[i]
        i += 1
        if i >= len(node_color_palette):
            i = 0

    return color_mapping


def draw_graph(
    graph=None,
    graph_filename: str = "graph",
    hide_condition: bool = False,
    node_font_size: int = 10,
    edge_font_size: int = 10,
    uniform_color: bool = False,
):

    try:
        # 함수 수집
        funcs = collect_functions(node)

        # 모든 함수를 하나의 리스트로 합치기
        all_funcs = []
        for func_list in funcs.values():
            all_funcs.extend(func_list)

        # 그래프에 있는 노드만 추출
        all_funcs = [func for func in all_funcs if func.__name__ in graph.nodes]

        # 엣지 수집
        edges = collect_edges(all_funcs)
        # 그래프에 있는 노드를 연결하는 엣지만 추출
        edges = [
            edge for edge in edges if edge[0] in graph.nodes and edge[1] in graph.nodes
        ]

        if not edges:
            print("No edges found in the functions")
            return

        print(f"Found {len(edges)} edges from {len(all_funcs)} functions")

        # 조건 정보 수집
        condition_info = []
        if not hide_condition:
            for func in all_funcs:
                descriptions = get_function_description(func)
                condition_info.extend(descriptions)

        # 루트 노드 찾기
        root_nodes = find_root_nodes(edges)
        print(f"Root nodes: {root_nodes}")

        # color mapping 정의
        color_mapping = {} if uniform_color else get_color_mapping(funcs, edges)

        draw_graph_with_graphviz(
            edges,
            condition_info,
            graph_filename,
            color_mapping,
            node_font_size=node_font_size,
            edge_font_size=edge_font_size,
        )

        # 엣지 정보 출력
        print("\nEdge information:")
        for start, end in edges:
            print(f"  {start} -> {end}")

    except Exception as e:
        print(f"Error drawing graph: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # 테스트 실행
    draw_graph()
