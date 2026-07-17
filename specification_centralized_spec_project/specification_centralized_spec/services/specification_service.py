import re

from bs4 import BeautifulSoup


def get_req_id_from_content(raw_content: str):
    """
    Extracts the req_id from the raw markdown content.
    """
    if not raw_content:
        return None
    for line in raw_content.splitlines():
        if "req_id:" in line.lower():
            return line.split(":", 1)[1].strip()
    return None


def parse_specification_content(raw_content: str):
    """
    Parses the raw markdown content to extract interface, specification content,
    and sub-specification contents.
    """
    req_id = None
    interface_content = None
    specification_content = None
    sub_spec_content = []

    if not raw_content:
        return req_id, interface_content, specification_content, sub_spec_content

    try:
        # Extract the req_id
        req_id = get_req_id_from_content(raw_content)

        # Extract the Interface section content
        interface_pattern = r"^###\s+Interface\s*(.*?)(?=^##\s|\Z)"
        interface_match = re.search(
            interface_pattern, raw_content, re.DOTALL | re.MULTILINE | re.IGNORECASE
        )
        if interface_match:
            interface_content = interface_match.group(1).strip()

        # Extract the Specification section content
        spec_pattern = r"^##\s+Specification\s*(.*?)(?=^##\s|\Z)"
        spec_match = re.search(
            spec_pattern, raw_content, re.DOTALL | re.MULTILINE | re.IGNORECASE
        )
        if spec_match:
            spec_content_raw = spec_match.group(1).strip()
            specification_content = spec_content_raw

            # Extract sub-specifications
            sub_specs = re.split(r"^###\s+(.+)$", spec_content_raw, flags=re.MULTILINE)

            for i in range(1, len(sub_specs), 2):
                sub_spec_content.append(
                    {
                        "header": {"text": sub_specs[i].strip()},
                        "content": sub_specs[i + 1].strip(),
                    }
                )
    except Exception as e:
        import traceback

        print(f"Exception in parse_specification_content: {e}")
        traceback.print_exc()

    return req_id, interface_content, specification_content, sub_spec_content



def parse_jama_specification_content(raw_content: str):
    """
    Parses the JAMA raw content to extract interface, specification content,
    and sub-specification contents.
    """
    interface_content = None
    specification_content = None
    sub_spec_content = []

    if not raw_content:
        return interface_content, specification_content, sub_spec_content

    try:
        soup = BeautifulSoup(raw_content, 'html.parser')

        # Find the "Interface" header (h3) and get its content
        interface_header = soup.find('h3', string=re.compile(r'^\s*Interface\s*$', re.IGNORECASE))
        if interface_header:
            #content_parts = [str(interface_header)]
            content_parts = []
            for element in interface_header.find_next_siblings():
                if element.name and element.name.startswith('h') and int(element.name[1]) <= 3:
                    break
                content_parts.append(str(element))
            interface_content = ''.join(content_parts).strip()

        # Find the "Specification" header (h2) and get its content
        spec_header = soup.find('h2', string=re.compile(r'^\s*Specification\s*$', re.IGNORECASE))
        if spec_header:
            # Extract content for the main specification section
            main_spec_content_parts = [str(spec_header)]
            for element in spec_header.find_next_siblings():
                if element.name == 'h2': # Stop at the next main section
                    break
                main_spec_content_parts.append(str(element))
            specification_content = ''.join(main_spec_content_parts).strip()

            # Extract sub-specifications (h3 sections within the Specification section)
            sub_headers = spec_header.find_next_siblings('h3')
            for i, sub_header in enumerate(sub_headers):
                # Check if this h3 is under the current h2
                if sub_header.find_previous('h2') != spec_header:
                    continue # Not a sub-header of our spec_header

                sub_spec_header_text = sub_header.get_text(strip=True)
                if sub_spec_header_text:
                    next_h3 = sub_headers[i + 1] if i + 1 < len(sub_headers) else None
                    sub_spec_content_parts = [str(sub_header)]
                    for element in sub_header.find_next_siblings():
                        if (element.name and element.name.startswith('h') and int(element.name[1]) <= 2) or (element == next_h3):
                            break
                        sub_spec_content_parts.append(str(element))
                    sub_spec_content.append({
                        "header": {"text": sub_spec_header_text},
                        "content": ''.join(sub_spec_content_parts).strip()
                    })

    except Exception as e:
        import traceback
        print(f"Exception in parse_jama_specification_content: {e}")
        traceback.print_exc()

    return interface_content, specification_content, sub_spec_content
