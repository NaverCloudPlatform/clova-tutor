# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

import argparse

import requests

from assistant.src.utils.load_utils import load_yaml


class VectorClient:
    def __init__(self, base_url):
        """
        Initializes the VectorClient with the given base URL.

        Note:
            For full implementation details, see:
            `edu-max-data/src/vector/service.py`
        """
        self.base_url = base_url
        self.headers_json = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.headers_multipart = {"accept": "application/json"}

    def get(self, index_name, docstore_id):
        """
        Get vector documents by their IDs from a specific index.

        Parameters:
            index_name (str): Name of the index to query.
            docstore_id (str): Single ID to retrieve.

        Returns:
            dict: Retrieved documents in JSON format.

        Raises:
            ValueError: If the request fails or returns a non-200 status code.
        """
        url = f"{self.base_url}/vector/get"

        payload = {"index_name": index_name, "ids": docstore_id}
        response = requests.post(url, data=payload, headers=self.headers_json)
        self._raise_on_error(response)
        return response.json()

    def search(
        self,
        index_name,
        query,
        search_type="mmr",
        k=2,
        filter_property=None,
        filter_value=None,
        all_of_filters=None,
    ):
        """
        Retrieval the vector index for documents similar to the query.

        Parameters:
            index_name (str): The name of the vector index to search
                            (e.g., Curriculum_course_2015, Problem_ebs_eng_be, etc.)
            query (str): The input text used for similarity search
            search_type (str, optional): Search algorithm to use, either "mmr" or "similarity" (default: "mmr")
            k (int, optional): Number of top results to return (default: 2)
            filter_property (str, optional): Metadata field to apply filtering on
            filter_value (str, optional): Value corresponding to the metadata field for filtering
            all_of_filters (dict, optional): Dictionary of metadata fields and their values for filtering

        Returns:
            dict: The search results as a JSON object

        Raises:
            ValueError: If the request fails or returns a non-200 status code
        """
        url = f"{self.base_url}/vector/search"
        headers = {}
        headers["accept"] = self.headers_json["accept"]
        headers["Content-Type"] = "application/json"

        payload = {
            "index_name": index_name,
            "query": query,
            "search_type": search_type,
            "k": k,
        }

        if filter_property:
            payload["filter_property"] = filter_property
        if filter_value:
            payload["filter_value"] = filter_value
        if all_of_filters:
            payload["all_of_filters"] = all_of_filters

        response = requests.post(url, json=payload, headers=headers)
        self._raise_on_error(response)
        return response.json()

    def create(self, index_name, file_path):
        """
        Creates a new vector index using data from the specified file.

        Parameters:
            index_name (str): Name of the new index to be created.
            file_path (str): Path to the CSV file containing the data.

        Returns:
            dict: API response in JSON format.

        Raises:
            ValueError: If the request fails or returns a non-200 status code.
        """
        url = f"{self.base_url}/vector/create"
        files = {"file": open(file_path, "rb")}
        payload = {"index_name": index_name}

        response = requests.post(
            url, files=files, data=payload, headers=self.headers_multipart
        )
        self._raise_on_error(response)
        return response.json()

    def add(self, index_name, file_path):
        """
        Adds documents to an existing vector index.

        Parameters:
            index_name (str): Name of the index to add documents to.
            file_path (str): Path to the CSV or parquet file containing new data.

        Returns:
            dict: API response in JSON format.

        Raises:
            ValueError: If the request fails or returns a non-200 status code.
        """
        url = f"{self.base_url}/vector/add"
        files = {"file": open(file_path, "rb")}
        payload = {"index_name": index_name}

        response = requests.post(
            url, files=files, data=payload, headers=self.headers_multipart
        )
        self._raise_on_error(response)
        return response.json()

    def delete(self, index_name, docstore_id):
        """
        Deletes specific documents from a vector index by ID.

        Parameters:
            index_name (str): Name of the index to delete from.
            docstore_id (str): Single ID to retrieve.

        Returns:
            dict: API response in JSON format.

        Raises:
            ValueError: If the request fails or returns a non-200 status code.
        """
        url = f"{self.base_url}/vector/delete"
        if isinstance(docstore_id, list):
            docstore_id = ",".join(docstore_id)

        payload = {"index_name": index_name, "docstore_ids": docstore_id}
        response = requests.post(url, data=payload, headers=self.headers_json)
        self._raise_on_error(response)
        return response.json()

    def _raise_on_error(self, response):
        if response.status_code != 200:
            raise ValueError(
                f"response.status_code: {response.status_code}, reason: {response.text}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="VectorClient CLI for vector DB operations.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create
    create_parser = subparsers.add_parser(
        "create",
        help="Create a new vector index",
        usage="python -m assistant.src.client.vector create <index_name> <file_path>\n\nExample:\n  $ python -m assistant.src.client.vector create Curriculum_course_2015 ./data/course_2015.csv",
    )
    create_parser.add_argument("index_name", help="Name of the index to create")
    create_parser.add_argument("file_path", help="Path to CSV file for creation")

    # Add
    add_parser = subparsers.add_parser(
        "add",
        help="Add documents to an existing index",
        usage="python -m assistant.src.client.vector add <index_name> <file_path>\n\nExample:\n  $ python -m assistant.src.client.vector add Curriculum_course_2015 ./data/course_2022.csv",
    )
    add_parser.add_argument("index_name", help="Name of the index to add to")
    add_parser.add_argument("file_path", help="Path to CSV or Parquet file")

    # Delete
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete documents by ID",
        usage="python -m assistant.src.client.vector delete <index_name> <docstore_id>\n\nExample:\n  $ python -m assistant.src.client.vector delete Curriculum_course_2015 1234-abc-5678",
    )
    delete_parser.add_argument("index_name", help="Name of the index")
    delete_parser.add_argument("docstore_id", help="Comma-separated document IDs")

    # Get
    get_parser = subparsers.add_parser(
        "get",
        help="Get a document by ID",
        usage="python -m assistant.src.client.vector get <index_name> <docstore_id>\n\nExample:\n  $ python -m assistant.src.client.vector get Curriculum_course_2015 1234-abc-5678",
    )
    get_parser.add_argument("index_name", help="Name of the index")
    get_parser.add_argument("docstore_id", help="Document ID")

    # Search
    search_parser = subparsers.add_parser(
        "search",
        help="Search documents in an index",
        usage=(
            "python -m assistant.src.client.vector search <index_name> <query> [--search_type mmr|similarity] [--k N] "
            "[--filter_property FIELD --filter_value VALUE]\n\n"
            "Example:\n"
            '  $ python -m assistant.src.client.vector search Curriculum_course_2015 "이차방정식"\n'
            '  $ python -m assistant.src.client.vector search Curriculum_course_2015 "이차방정식" --k 5 --search_type similarity --filter_property grade --filter_value 3'
        ),
    )
    search_parser.add_argument("index_name", help="Name of the index")
    search_parser.add_argument("query", help="Query text")
    search_parser.add_argument(
        "--search_type",
        default="mmr",
        choices=["mmr", "similarity"],
        help="Search type (default: mmr)",
    )
    search_parser.add_argument(
        "--k", type=int, default=2, help="Number of results to return (default: 2)"
    )
    search_parser.add_argument(
        "--filter_property", help="Optional metadata field to filter on"
    )
    search_parser.add_argument("--filter_value", help="Value for the filter property")

    args = parser.parse_args()
    client = VectorClient(
        base_url=load_yaml("assistant/api_info.yaml")["api-server"]["data-server-url"]
    )

    try:
        if args.command == "create":
            result = client.create(args.index_name, args.file_path)
        elif args.command == "add":
            result = client.add(args.index_name, args.file_path)
        elif args.command == "delete":
            result = client.delete(args.index_name, args.docstore_id.split(","))
        elif args.command == "get":
            result = client.get(args.index_name, args.docstore_id)
        elif args.command == "search":
            result = client.search(
                args.index_name,
                args.query,
                args.search_type,
                args.k,
                args.filter_property,
                args.filter_value,
            )
        else:
            parser.print_help()
            return

        print("결과:")
        if isinstance(result, list):
            for row in result:
                print("----------------------" * 3)
                print(row)
        else:
            print(result)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
