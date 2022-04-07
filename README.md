# lynis-bridge

Accept lynis-report.dat files (upload), transform it into json and put it into a mariadb to visualize the result with grafana.

![lynis_grafana](lynis_grafana.png)

## notes

When using lynis-cron, you can post the result to your lynis-bridge with curl (_yes, the user-agent must be set to `lynis-bridge`, otherwise the lynis-bridge will response http code 403_).

```
curl -A "lynis-bridge" -F data=@lynis-report.dat http://<lynis-bridge>:8080/upload
curl -A "lynis-bridge" -F data=@report.dat http://172.16.1.180:30007/upload
```

# database

Currently only Mariadb >= 10.3 is supported.  
The table `reports` is using `WITH SYSTEM VERSIONING`. So you got a report history about you hosts.  
You just need to query them ;)

# credits.

`lynis-report-converter.pl` is taken from https://github.com/d4t4king/lynis-report-converter

# SCM

| **host** | **category** |
| --- | --- |
| https://git.osuv.de/m/lynis-bridge | origin |
| https://gitlab.com/markuman/lynis-bridge | pull mirror |
| https://github.com/markuman/lynis-bridge | push mirror |
