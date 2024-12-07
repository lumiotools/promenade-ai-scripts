import os
import json

def check_and_update_content(content):
    if content is None:
        return ""
    error_keywords = ["Error", "404", "not found"]
    if any(keyword.lower() in content.lower() for keyword in error_keywords):
        return ""
    return content

def process_json_files(directory):
    files_with_issues = []

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in file {filename}: {e}")
                    continue

            symbol = data.get("symbol", "")
            structured_data = data.get("structured_data", [])
            file_changed = False

            for section in structured_data:
                for link in section.get("links", []):
                    original_content = link.get("content", "")
                    updated_content = check_and_update_content(original_content)
                    if original_content != updated_content:
                        link["content"] = updated_content
                        file_changed = True

            if file_changed:
                with open(filepath, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                files_with_issues.append((filename, "Changed"))
            else:
                files_with_issues.append((filename, "No Change"))

    return files_with_issues

if __name__ == "__main__":
    output_directory = './output'
    results = process_json_files(output_directory)
    for filename, status in results:
        print(f"{filename}: {status}")