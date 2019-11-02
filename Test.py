import requests

from Net.DependencyNet import DependencyNet

if __name__ == '__main__':
    url = 'https://mvnrepository.com/artifact/org.wso2.carbon.identity.framework/org.wso2.carbon.directory.server.manager'
    print(DependencyNet.fetch_license_2(url))
