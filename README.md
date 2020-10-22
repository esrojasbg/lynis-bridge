# lynis-bridge

Accept lynis-report.dat files (upload), transform it into json and put it into a mariadb to visualize the result with grafana.

![lynis_grafana](lynis_grafana.png)

## notes

When using lynis-cron, you can post the result to your lynis-bridge with curl.

```
curl -F data=@lynis-report.dat http://<lynis-bridge>:8080/upload
```

# database

Currently only Mariadb >= 10.3 is supported.  
The table `reports` is using `WITH SYSTEM VERSIONING`. So you got a report history about you hosts.  
You just need to query them ;)

# credits.

`lynis-report-converter.pl` is taken from https://github.com/d4t4king/lynis-report-converter