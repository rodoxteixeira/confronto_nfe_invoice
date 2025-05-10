import xml.etree.ElementTree as ET

def processar(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ns = {"ns": "http://www.portalfiscal.inf.br/nfe"}

    itens = []
    total_pares = 0
    total_nota = 0.0

    for det in root.findall(".//ns:det", ns):
        nItem = det.attrib.get("nItem", "")  # captura o atributo nItem
        prod = det.find("ns:prod", ns)

        if prod is not None:
            cProd_completo = prod.findtext("ns:cProd", default="", namespaces=ns)
            cProd = cProd_completo.split(".")[0]  # simplifica cProd
            xProd_raw = prod.findtext("ns:xProd", default="", namespaces=ns)
            NCM = prod.findtext("ns:NCM", default="", namespaces=ns)
            CFOP = prod.findtext("ns:CFOP", default="", namespaces=ns)
            uCom = prod.findtext("ns:uCom", default="", namespaces=ns)
            qCom = prod.findtext("ns:qCom", default="0", namespaces=ns)
            vUnCom = prod.findtext("ns:vUnCom", default="0", namespaces=ns)
            vProd = prod.findtext("ns:vProd", default="0", namespaces=ns)
            nItemPed = prod.findtext("ns:nItemPed", default="", namespaces=ns)

            # Reconstrução de xProd no formato REF - COR - TAM
            xProd_partes = xProd_raw.split("MOD")[-1].strip().split()
            if len(xProd_partes) >= 3:
                ref = xProd_partes[0]
                cor = xProd_partes[1]
                numero = xProd_partes[2]
                xProd = f"{ref} - {cor} - {numero}"
            else:
                xProd = xProd_raw.strip()

            try:
                qCom = float(str(qCom).replace(",", "."))
                vUnCom = float(str(vUnCom).replace(",", "."))
                vProd = float(str(vProd).replace(",", "."))
            except:
                qCom = vUnCom = vProd = 0.0

            total_pares += qCom
            total_nota += vProd

            itens.append({
                "nItem": int(nItem) if nItem.isdigit() else None,
                "ref": cProd,
                "xProd": xProd,
                "ncm": NCM,
                "cfop": CFOP,
                "unidade": uCom,
                "total pares": qCom,
                "unit price": vUnCom,
                "valor total": vProd,
                "item pedido": nItemPed
            })

    resumo = {
        "itens": len(itens),
        "total pares": total_pares,
        "valor total xml": round(total_nota, 2)
    }

    return itens, resumo
