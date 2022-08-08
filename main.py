#!/usr/bin/env python3


import sys, os, shutil, readline, \
    fire, markdown
from bs4 import BeautifulSoup
from simplegmail import Gmail


# TODO: Refactor, and use `stoyled` functions to make it more fancy.
SCRIPT_DIR = os.path.dirname(__file__)
SECRET_FILE = os.path.join(SCRIPT_DIR, 'client_secret.json')
if not os.path.isfile(SECRET_FILE):
    print('[-] Warning: `client_secret.json` not found, please select one.')
    client_secret_path = os.path.expanduser( input("[<] Enter path to you client_secret*.json: ") )
    client_secret_filename = client_secret_path.split('/')[-1]
    shutil.copy2(client_secret_path, SCRIPT_DIR)
    shutil.move(os.path.join(SCRIPT_DIR, client_secret_filename), SECRET_FILE)


def parse_carbon_copy(ccs):
    if os.path.isfile(ccs):
        ccs = open(ccs, 'r').read()
        ccs = ccs.strip().split('\n')
        if len(ccs) > 1:
            return ccs
    if ',' in ccs:
        if len(ccs.split(',')) > 1:
            ccs = ccs.split(',')
    return ccs


def parse_attachments(attachments):
    if os.path.isfile(attachments):
        attachments = [attachments]
    else:
        attachments = []; _attachments = attachments.split(',')
        if len(_attachments) > 1:
            attachment = _attachments
            if not os.path.isfile(attachment):
                raise ValueError(f"[-] File not found: The file you're trying to attach isn't found at {attachment}")
            attachments += [attachment]
        else:
            raise ValueError(f"[-] File not found: The file you're trying to attach isn't found at {attachments}")
    return attachments


def mail(to='', sender='', subject='', markdown_body='', markup_body='', plain_body='', cc='', bcc='', attachments=''):
    """
    Required arguments: (to, sender, subject, { markup_body or plain_body })
    Optional arguments: (cc, bcc, attachments)
    Note that,
        you must use a comma-separated filenames attachments or just a single filename to an attachment for using it.
    And,
        you're supposed to use a comma-separated values for cc and bcc or reference to a file with E-mails separated with new line or is a single-line comma-separated E-mails.
    """
    if not ( to and sender and subject and ( markdown_body or markup_body or plain_body ) ):
        raise ValueError("[-] Missing required arguments: (to, sender, subject, { markup_body or plain_body })")
    if markdown_body: markup_body = markdown.markdown( markdown_body ); plain_body = BeautifulSoup(markup_body, 'lxml').text
    if attachments: attachments = parse_attachments(attachments)
    if plain_body and not markup_body: markup_body = plain_body  # This makes sure that Gmail will send the plain text body.
    if bcc: bcc = parse_carbon_copy(bcc)
    if cc: cc = parse_carbon_copy(cc)
    params = {
        "to": to,
        "sender": sender,
        "cc": cc,
        "bcc": bcc,
        "subject": subject,
        "msg_html": markup_body,
        "msg_plain": plain_body,
        "attachments": attachments,
        "signature": True,
    }; gmail = Gmail()
    return gmail.send_message(**params)


def main():
    subject = input("[Subject]: ")
    to = input("[To]: ")
    sender = input("[Sender]: ")
    cc = input("[CC] <Filename/CSV/Leave empty if none>: ")
    bcc = input("[BCC] <Filename/CSV/Leave empty if none>: ")
    attachments = input("[Attachments] <CSV/Leave empty if none>: ")
    print("-Select the type of body you would like to send-")
    _options = ['Markdown', 'Markup', 'Plaintext']
    for _option in _options:
        print(f"{_options.index(_option) + 1}. {_option}")
    body_type = input("[<] Selection [1]-> ")
    print("-Select how would you like to send the body-")
    _options = ['Loading mail body from file.', 'Entering mail body here itself.']
    for _option in _options:
        print(f"{_options.index(_option) + 1}. {_option}")
    input_type = input("[<] Selection [1]-> ")
    if input_type == '1':
        body = open(input("[<] Enter the path to the file: "), 'r').read()
    elif input_type == '2':
        # TODO: Using getch() to read the body from the user (for cool key-bindings to work!)
        print("[<] Enter you mail body [use Ctrl+D instead of Enter when done]: ")
        body = sys.stdin.read()
    else:
        raise ValueError("[-] Invalid selection.")
    print("[+] Sending mE-mail...")
    if body_type == '1':
        return mail(to, sender, subject, markdown_body=body, cc=cc, bcc=bcc, attachments=attachments)
    elif body_type == '2':
        return mail(to, sender, subject, markup_body=body, cc=cc, bcc=bcc, attachments=attachments)
    elif body_type == '3':
        return mail(to, sender, subject, plain_body=body, cc=cc, bcc=bcc, attachments=attachments)
    else:
        raise ValueError("[-] Invalid selection.")


if __name__ == '__main__':
    try:
        print('[+] Starting m-mailer...')
        fired = fire.Fire(main)
        if not fired:
            raise Exception("[-] Looks like something went wrong, but I'm not at all sure on what's that.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[-] Exiting m-mailer...")
        sys.exit(0)
    except EOFError:
        print("\n[-] Exiting m-mailer...")
        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)
