import requests
from bs4 import BeautifulSoup

import Message
from util.ParamUtil import ParamUtil


class DependencyNet(object):

    # 从version界面提取License
    @staticmethod
    def extract_from_version(version_response):
        version_response.encoding = 'utf-8'
        soup = BeautifulSoup(version_response.text, "html.parser")

        version_section_list = soup.findAll(name="div", attrs={'class': 'version-section'})

        for version_section in version_section_list:
            if version_section.find(name='h2').text == 'Licenses':
                license_list = list()
                # <div class="version-section"><h2>Licenses</h2><table class="grid" width="100%"><thead><tr><th style="width: 16em;">License</th><th>URL</th></tr></thead><tbody><tr><td>The Apache Software License, Version 2.0</td><td><a href="http://www.apache.org/licenses/LICENSE-2.0.txt" rel="nofollow">
                # http://www.apache.org/licenses/LICENSE-2.0.txt
                # </a></td></tr></tbody></table></div>
                tbody_soup = version_section.find(name='tbody')
                tr_list_soup = tbody_soup.findAll(name='tr')
                for tr_soup in tr_list_soup:
                    license_list.append(tr_soup.find(name='td').text)
                return license_list
        return None

    @staticmethod
    def fetch_license(version_url, artifact_url, has_version):
        # 爬取规则：
        # 如果has_version:
        # 1. 爬取 version_url,
        #   1.1 如果能爬到,code=200，直接得到结果,返回
        #   1.2 爬取结果为404，说明可能没有这个依赖或没有这个version
        #       1.2.1 爬取 artifact_url,爬取成功，说明有这个jar包，但没有version这个版本。
        #       1.2.2 爬取 artifact_url，404，说明不存在这个jar包
        # 否则，直接跳到1.2

        if has_version:
            version_response = requests.get(version_url)
            if version_response.status_code == 200:
                # 爬到数据，解析数据
                license_list = DependencyNet.extract_from_version(version_response)
            elif version_response.status_code == 404:
                # 没有这个版本的依赖，需要重新爬取artifact
                artifact_response = requests.get(artifact_url)
                if artifact_response.status_code == 200:
                    DependencyNet.extract_from_artifact(artifact_response)
                elif artifact_response.status_code == 404:
                    # 不存在这个jar包
                    pass
        else:
            # 没有version，只能爬取artifact_url
            artifact_response = requests.get(artifact_url)
            if artifact_response.status_code == 200:
                DependencyNet.extract_from_artifact(artifact_response)
            elif artifact_response.status_code == 404:
                # 不存在这个jar包
                pass

    @staticmethod
    def fetch_dependency_license(form):
        # 抽取参数
        param = ParamUtil.extractParam(form)
        groupId = param['groupId']
        artifactId = param['artifactId']
        version = param['version']
        # type = param['type']

        base_url = 'https://mvnrepository.com/artifact/'

        artifact_url = base_url + groupId + '/' + artifactId
        version_url = artifact_url + '/' + version

        has_version = len(version_url) > 0
        # 得到参数后由爬虫获取信息

        DependencyNet.fetch_license(version_url, artifact_url, has_version)

    @staticmethod
    def fetch_dependency_license2(form):
        # 抽取参数
        param = ParamUtil.extractParam(form)
        groupId = param['groupId']
        artifactId = param['artifactId']
        base_url = 'https://mvnrepository.com/artifact/'

        artifact_url = base_url + groupId + '/' + artifactId
        try:
            status_code, message, content = DependencyNet.fetch_license_2(artifact_url)
            return status_code, message, content
        except Exception:
            return 200, Message.server_internet_error, ''

    @staticmethod
    def fetch_license_2(url):
        artifact_response = requests.get(url)
        if artifact_response.status_code == 200:
            artifact_response.encoding = 'utf-8'
            soup = BeautifulSoup(artifact_response.text, "html.parser")
            license_soup = soup.find(name='span', attrs={'class': 'b lic'})
            if license_soup is not None:
                license_text = license_soup.text
                return 200, Message.success, license_text
            else:
                return 200, Message.no_license, None
        elif artifact_response.status_code == 404:
            return 404, Message.no_dependency, None
