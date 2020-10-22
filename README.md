# lynis-bridge

Accept lynis-report.dat files (upload), transform it into json and put it into a mariadb to visualize the result with grafana.

![lynis_grafana](lynis_grafana.png)

## notes

```
curl -F data=@lynis-report.dat http://localhost:8080/upload
```

# credits.

`lynis-report-converter.pl` is taken from https://github.com/d4t4king/lynis-report-converter