package org.example;

import com.itextpdf.text.*;
import com.itextpdf.text.pdf.*;
import com.itextpdf.tool.xml.ElementHandler;
import com.itextpdf.tool.xml.Writable;
import com.itextpdf.tool.xml.XMLWorkerHelper;
import com.itextpdf.tool.xml.pipeline.WritableElement;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class Main {
    private static String FILE = "invoice.pdf";
    private static float FULL_WIDTH = 720f;

    public static void main(String[] args) {
        try {
            Document document = new Document(PageSize.LETTER.rotate(), 36, 36, 100, 40);
            PdfWriter writer = PdfWriter.getInstance(document, new FileOutputStream(FILE));
            writer.setPageEvent(new HeaderFooterPageEvent());
            document.open();

            // Add Prolog
            addProlog(writer, document);

            // Create table
            PdfPTable table = createTable();
            table.setTotalWidth(FULL_WIDTH);

            // Add Items
            PdfContentByte canvas = writer.getDirectContent();
            addRows(0, 1, table);
            table.writeSelectedRows(0, -1, 0, 3, 36, 230, canvas);

            document.newPage();
            addRows(2, 6, table);
            table.writeSelectedRows(0, -1, 3, 9, 36, 450, canvas);

            document.newPage();
            addRows(7, -1, table);
            table.writeSelectedRows(0, -1, 9, -1, 36, 450, canvas);

            document.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static PdfPTable createTable() throws DocumentException {
        // columns width
        PdfPTable table = new PdfPTable(9); // column count is 9

        float[] columnWidths = {1f, 2.7f, 8f, 3f, 1f, 2f, 3.5f, 2f, 2.3f};
        table.setWidths(columnWidths);


        return table;
    }

    private static void addRows(int start, int end, PdfPTable table) {
        JSONParser jsonParser = new JSONParser();
        try {
            JSONArray jsonArray = (JSONArray) jsonParser.parse(new FileReader("src/main/resources/items.json"));

            // add header of table piece
            addHeader(table);
            if (end == -1)
                end = jsonArray.size() -1;

            // add rows
            for(int i =start ; i <= end ;i ++) {
                JSONObject obj = (JSONObject) jsonArray.get(i);
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("line", "#"))));
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("hp-id", ""))));
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("desc", ""))));
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("part", ""))));
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("qty", "0"))));
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("uom", ""))));
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("date", ""))));
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("uprice", "$0"))));
                table.addCell(new PdfPCell(new Phrase((String) obj.getOrDefault("tprice", "$0"))));
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        } catch (ParseException e) {
            throw new RuntimeException(e);
        }
    }

    private static void addHeader(PdfPTable table) {
        Font bold = new Font(Font.FontFamily.UNDEFINED, 10, Font.BOLD);
        BaseColor headerColor = new BaseColor(170, 206, 235); // primary color
        PdfPCell cell;

        cell = new PdfPCell(new Phrase("Line", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);

        cell = new PdfPCell(new Phrase("H&P ID", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);

        cell = new PdfPCell(new Phrase("Description", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);

        cell = new PdfPCell(new Phrase("Part No.", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);

        cell = new PdfPCell(new Phrase("Qty", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);

        cell = new PdfPCell(new Phrase("UOM", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);

        cell = new PdfPCell(new Phrase("Date", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);

        cell = new PdfPCell(new Phrase("Price/U", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);

        cell = new PdfPCell(new Phrase("Price", bold));
        cell.setBackgroundColor(headerColor);
        table.addCell(cell);
    }
    private static void addProlog(PdfWriter writer, Document document) throws IOException {
        // Read prolog.html
        ArrayList<Element> htmlElements = new ArrayList<>();
        InputStream htmlStream = Main.class.getResourceAsStream("/prolog.html");
        XMLWorkerHelper.getInstance().parseXHtml(new ElementHandler() {
            @Override
            public void add(final Writable writable) {
                if (writable instanceof WritableElement) {
                    htmlElements.addAll(((WritableElement) writable).elements());
                }
            }
        }, htmlStream, StandardCharsets.UTF_8);

        // Draw Header
        PdfContentByte cb = writer.getDirectContent();

        float start = 60f;
        float gap = 4f;

        for (Element element : htmlElements) {
            try {
                ColumnText ct = new ColumnText(cb);

                ct.setSimpleColumn(document.left() , document.top() -450f, document.right(), document.top() -start);

                ct.addElement(element);
                float startY = ct.getYLine();
                ct.go();
                float endY = ct.getYLine();  // after rendering
                float height = startY - endY;
                start = height + start + gap;
            } catch (DocumentException e) {
                e.printStackTrace();
            }
        }
    }
}