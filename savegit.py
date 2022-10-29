# -*- coding: utf-8 -*-
#!/usr/bin/env python

from argparse import ArgumentParser, Namespace
from collections import defaultdict
from datetime import datetime
import time
import logging
import os
import requests
from requests.exceptions import ConnectTimeout
import zipfile
import shutil


class GitHub:
    """
    GitHub interaction class
    """
    def __init__(self, args: Namespace) -> None:
        # class object initialization
        self.args = args

        self.save_path = self.args.path if self.args.path else "./"
        self.save_path = self.save_path[:-1] if self.save_path[-1] == "/" else self.save_path

        self.url = "https://api.github.com/"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.args.token}"
        }

        logging.info(
            "\n\n\t🚀🚀🚀🚀\n\tThe project was created by AlekseevDanil\n\tThanks for using!\n\t🚀🚀🚀🚀\n\n"
        )

    def check_oauth(self):
        # validation of the token and user information
        user_request = requests.get(
            url=self.url+"user",
            headers=self.headers
        ).json()
        if not "login" in user_request:
            logging.critical("Check if the token is correct, the user could not be determined.")
        else:
            return True
    
    def backup(self) -> None:
        # get all user information
        user_request = requests.get(
            url=self.url+"user",
            headers=self.headers
        ).json()
        username = user_request["login"]
        logging.info(f"GitHub user: {username}")
        
        logging.debug(f"Loading information, please wait for the full load...")

        # get information about repositories + all branches in the repository
        repositories_request = requests.get(
            url=self.url+"search/repositories?q=user:"+username,
            headers=self.headers
        ).json()
        repositories = defaultdict(list)
        for rep_name in repositories_request["items"]:
            branches_request = requests.get(
                url=self.url+f"repos/{username}/{rep_name['name']}/branches",
                headers=self.headers
            ).json()
            for branch in branches_request:
                repositories[rep_name['name']].append(branch["name"])
        logging.info(f"Total number of repositories: {len(repositories)}")

        # all information about the user's gists
        gists_request = requests.get(
            url=self.url+f"users/{username}/gists",
            headers=self.headers
        ).json()
        gists = {url["html_url"].split("/")[-1]: list(url["files"].items())[0][0] for url in gists_request}
        logging.info(f"Total number of gists: {len(gists)}\n")

        # create directories for backup
        main_path = f"{self.save_path}/GitHub-{username}-"\
                    f"{str(datetime.now()).replace(' ', 'T').replace('-', '.').replace(':', '-')}"
        os.mkdir(main_path)
        os.mkdir(main_path+"/repositories/")
        os.mkdir(main_path+"/gists/")
        main_path = os.path.realpath(main_path)

        def download_content(url: str, message: str):
            for _ in range(5):
                try:
                    logging.debug(message)
                    return requests.get(url=url, headers=self.headers)
                except ConnectTimeout:
                    logging.error("Connection refused by the server. Reconnect after 10 seconds.")
                    time.sleep(10)
                    continue

        # download repositories
        logging.debug(f"Downloading all user's repositories...")
        for index, rep_name in enumerate(repositories):
            for branch in repositories[rep_name]:
                req = download_content(
                    url=self.url+f"repos/{username}/{rep_name}/zipball/{branch}",
                    message=f"{index+1}/{len(repositories)} - Repository download - \"{rep_name}/{branch}\""
                )
                if req.status_code == 200:
                    if not os.path.isdir(f'{main_path}/repositories/{rep_name}/'): 
                        os.mkdir(f"{main_path}/repositories/{rep_name}/")
                    with open(f'{main_path}/repositories/{rep_name}/{branch.replace("/", "-")}.zip', 'wb') as files_path:
                        files_path.write(req.content)
                else:
                    logging.error(f"Failed to reach the repository: {rep_name}. Status: {req.status_code}")

        # download gists
        logging.debug(f"Downloading all user's gists...")
        for index, gist_id in enumerate(gists):
            req = download_content(
                    url=self.url+f"gists/{gist_id}",
                    message=f"{index+1}/{len(gists)} - Gist download - \"{gists[gist_id]}\""
                )
            if req.status_code == 200:
                with open(main_path+"/gists/"+gists[gist_id], "w") as files_path:
                    files_path.write(req.json()["files"][gists[gist_id]]["content"])
            else:
                logging.error(f"Failed to reach the gist: {gists['gists_id']}. Status: {req.status_code}")

        # archiving backups
        shutil.make_archive(base_name=main_path, format="zip", root_dir=main_path)
        shutil.rmtree(path=main_path)

        logging.debug(f"✅ Backup completed successfully. The result is saved in  {main_path}.zip")


if __name__ == "__main__":
    # geting options from command line
    parser = ArgumentParser(description='Add description letter')
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument("-p", "--path", 
                          dest="path",
                          help="directory where backups are saved", 
                          metavar="PATH")
    optional.add_argument("-q", "--quiet",
                          default=False,
                          action="store_true", 
                          dest="quiet",
                          help="don't logging to stdout")
    required = parser.add_argument_group('required arguments')
    required.add_argument("-t", "--token",
                          dest="token",
                          help="api token of your github", 
                          metavar="TOKEN", 
                          required=True)
    args = parser.parse_args()

    # script logging configuration
    logging.basicConfig(
        format='%(asctime)s : [%(levelname)s] %(message)s',
        level=10 if not args.quiet else 50
    )
    logging.getLogger("urllib3").setLevel('ERROR')

    # making a GitHub Backup
    gh = GitHub(args=args)
    if gh.check_oauth():
        gh.backup()
