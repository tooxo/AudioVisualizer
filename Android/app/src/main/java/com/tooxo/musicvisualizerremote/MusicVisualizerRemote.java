package com.tooxo.musicvisualizerremote;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.text.Editable;
import android.text.InputType;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.Switch;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MusicVisualizerRemote extends AppCompatActivity {

    String ip = "";
    Boolean outputBool = true;
    int outputDevice = -1;
    int inputDevice = -1;
    double delay = 0.0;
    Boolean lightsOn = true;
    String chromecastname = "";
    String input_type = "AUX";
    String output_type = "AUX";
    int cutthreshhold = 0;

    OkHttpClient client = new OkHttpClient();

    public String getSettings(String address) {
        String resp;
        Request request = new Request.Builder()
                .url("http://" + address + "/req_settings")
                .build();
        try (Response response = client.newCall(request).execute()) {
            assert response.body() != null;
            resp = response.body().string();
            return resp;
        } catch (IOException e) {
            resp = e.toString();
            return resp;
        }
    }

    public String setSettings(JSONObject json, String address) {
        String resp;
        MediaType JSON = MediaType.parse("application/json; charset=utf-8");
        RequestBody body = RequestBody.create(JSON, json.toString());
        Request request = new Request.Builder()
                .url("http://" + address + "/set_settings")
                .post(body)
                .build();

        try (Response re = client.newCall(request).execute()) {
            assert re.body() != null;
            resp = re.body().string();
            if (resp.equals("Done.")) {
                return "Done, No errors occured.";
            } else {
                return resp;
            }
        } catch (IOException io) {
            return io.toString();
        }
    }

    public void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        setContentView(R.layout.main);
        Spinner inputMode = findViewById(R.id.inputMode);
        Spinner outputMode = findViewById(R.id.outputMode);
        EditText thresholdEdit = findViewById(R.id.threshold);


        /*
            ON SWITCH
         */

        Switch sw = findViewById(R.id.switch1);
        sw.setOnCheckedChangeListener((buttonView, isChecked) -> lightsOn = isChecked);

        /*
            IP SELECTION
         */

        final EditText ipselec = findViewById(R.id.editIp);
        SharedPreferences sh = PreferenceManager.getDefaultSharedPreferences(this);
        String savedIp = sh.getString("ip", "");
        ip = savedIp;
        ipselec.setText(savedIp);
        Context context = this;
        ipselec.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                ip = ipselec.getText().toString();
                SharedPreferences.Editor editor = PreferenceManager.getDefaultSharedPreferences(context).edit();
                editor.putString("ip", ip);
                editor.apply();
            }

            @Override
            public void afterTextChanged(Editable s) {
            }
        });

        /*
            Get button
         */

        Button get = findViewById(R.id.getSettings);
        get.setOnClickListener(v -> new Thread(() -> {

            String ret = getSettings(ip);
            try {
                JSONObject object = new JSONObject(ret);
                runOnUiThread(() -> {
                    try {
                        sw.setChecked(object.getBoolean("lightson"));
                        lightsOn = object.getBoolean("lightson");
                    } catch (JSONException js) {
                        js.printStackTrace();
                    }
                    EditText input = findViewById(R.id.auxInDevice);
                    try {
                        switch (object.getString("input_type")) {
                            case "Spotify":
                                inputMode.setSelection(1, false);
                                input.setHint("WRONG INPUT TYPE");
                                input.setEnabled(false);
                                input_type = "Spotify";
                                inputDevice = 0;
                                break;
                            case "AUX":
                                inputMode.setSelection(0, false);
                                int q = object.getInt("inputdevice");
                                input.setText(String.valueOf(q));
                                inputDevice = q;
                                input_type = "AUX";
                                input.setEnabled(true);
                                break;
                        }
                    } catch (JSONException e) {
                        new AlertDialog.Builder(context)
                                .setTitle("Update")
                                .setMessage("Update Failed " + e)
                                .show();
                    }
                    EditText output = findViewById(R.id.auxOutDevice);
                    try {
                        switch (object.getString("output_type")) {
                            case "AUX":
                                outputMode.setSelection(0, false);
                                int q = object.getInt("outputdevice");
                                output.setHint("AUX OUT Device");
                                output_type = "AUX";
                                output.setText(String.valueOf(q));
                                output.setEnabled(true);
                                output.setInputType(InputType.TYPE_CLASS_NUMBER);
                                outputDevice = q;
                                break;
                            case "Chromecast":
                                outputMode.setSelection(1, false);
                                output.setHint("Chromecast Device Name");
                                output.setEnabled(true);
                                output_type = "Chromecast";
                                output.setText(object.getString("chromecastname"));
                                chromecastname = object.getString("chromecastname");
                                output.setInputType(InputType.TYPE_CLASS_TEXT);
                                outputDevice = -2;
                                break;
                            case "None":
                                outputMode.setSelection(2, false);
                                output.setHint("NO SOUND OUTPUT");
                                output.setEnabled(false);
                                output_type = "None";
                                outputDevice = -2;
                                break;
                        }
                    } catch (JSONException e) {
                        new AlertDialog.Builder(context)
                                .setTitle("Update")
                                .setMessage("Update Failed " + e)
                                .show();
                    }
                    EditText du = findViewById(R.id.delay);
                    try {
                        double d = object.getDouble("delay");
                        delay = d;
                        du.setText(String.valueOf(d));
                        output.setEnabled(true);
                    } catch (JSONException e) {
                        new AlertDialog.Builder(context)
                                .setTitle("Update")
                                .setMessage("Update Failed " + e)
                                .show();
                    }

                    try {
                        int d = object.getInt("cutthreshold");
                        cutthreshhold = d;
                        thresholdEdit.setText(String.valueOf(d));
                    } catch (JSONException e) {
                        new AlertDialog.Builder(context)
                                .setTitle("Update")
                                .setMessage("Update Failed " + e)
                                .show();
                    }

                    new AlertDialog.Builder(context)
                            .setTitle("Update")
                            .setMessage("Updated From Web!")
                            .show();
                });
            } catch (JSONException e) {
                e.printStackTrace();
                runOnUiThread(() -> new AlertDialog.Builder(context)
                        .setTitle("Update")
                        .setMessage("Update Failed " + e)
                        .show());
            }
        }).start());


        /*
            INPUT ARRAY
         */

        final ArrayList<String> inputArray = new ArrayList<>();
        inputArray.add("AUX IN");
        inputArray.add("Spotify Connect");
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, R.layout.support_simple_spinner_dropdown_item, inputArray);
        adapter.setDropDownViewResource(R.layout.support_simple_spinner_dropdown_item);
        inputMode.setAdapter(adapter);

        inputMode.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
                String input = inputArray.get(i);
                if (input.equals("Spotify Connect")) {
                    EditText s = findViewById(R.id.auxInDevice);
                    s.setHint("WRONG INPUT MODE");
                    inputDevice = 0;
                    input_type = "Spotify";
                    s.setEnabled(false);
                } else {
                    EditText s = findViewById(R.id.auxInDevice);
                    s.setHint("AUX IN Device");
                    inputDevice = 0;
                    s.setText("0");
                    input_type = "AUX";
                    s.setEnabled(true);
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> adapterView) {
            }
        });

        /*
            OUTPUT ARRAY
         */

        final ArrayList<String> outputArray = new ArrayList<>();
        outputArray.add("AUX OUT");
        outputArray.add("Chromecast Out (heavy delay)");
        outputArray.add("No Sound output");
        ArrayAdapter<String> adapter1 = new ArrayAdapter<>(this, R.layout.support_simple_spinner_dropdown_item, outputArray);
        adapter1.setDropDownViewResource(R.layout.support_simple_spinner_dropdown_item);
        outputMode.setAdapter(adapter1);

        outputMode.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
                String output = outputArray.get(i);
                EditText s = findViewById(R.id.auxOutDevice);
                switch (output) {
                    case "AUX OUT":
                        s.setHint("AUX OUT Device");
                        s.setEnabled(true);
                        outputBool = true;
                        output_type = "AUX";
                        s.setInputType(InputType.TYPE_CLASS_NUMBER);
                        break;
                    case "Chromecast Out (heavy delay)":
                        s.setHint("Chromecast Device Name");
                        s.setEnabled(true);
                        s.setInputType(InputType.TYPE_CLASS_TEXT);
                        outputBool = false;
                        output_type = "Chromecast";
                        break;
                    case "No Sound output":
                        s.setHint("NO SOUND OUTPUT");
                        s.setEnabled(false);
                        outputBool = false;
                        output_type = "None";
                        break;
                }
            }

            @Override
            public void onNothingSelected(AdapterView<?> adapterView) {
            }
        });


        /*
            DELAY FIELD
         */

        final EditText delayTx = findViewById(R.id.delay);
        delayTx.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                if (delayTx.getText().length() > 0 && !delayTx.getText().toString().equals(".")) {
                    delay = Double.valueOf(delayTx.getText().toString());
                }
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });


        /*
            AVAILABLE DEVICES
         */

        Button available = findViewById(R.id.available);
        available.setOnClickListener(v -> new Thread(() -> {
            String resp;
            Request request = new Request.Builder()
                    .url("http://" + ip + "/devices")
                    .build();
            try (Response response = client.newCall(request).execute()) {
                assert response.body() != null;
                resp = response.body().string();
            } catch (IOException e) {
                resp = e.toString();
            }

            AlertDialog.Builder dialog = new AlertDialog.Builder(context)
                    .setTitle("Available Devices")
                    .setMessage(resp);
            runOnUiThread(dialog::show);
        }).start());

        /*
            AUX IN DEVICE
         */

        EditText inDevice = findViewById(R.id.auxInDevice);
        inDevice.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                try {
                    inputDevice = Integer.valueOf(s.toString());
                } catch (Exception e) {
                    inputDevice = -1;
                }
            }

            @Override
            public void afterTextChanged(Editable s) {
            }
        });

        /*
            AUX OUT DEVICE
         */

        EditText outDevice = findViewById(R.id.auxOutDevice);
        outDevice.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                Log.v("fick", output_type);
                if (!output_type.equals("Chromecast")) {
                    try {
                        outputDevice = Integer.valueOf(s.toString());
                    } catch (Exception e) {
                        outputDevice = -1;
                    }
                }else {
                    Log.v("foc", "you");
                    outputDevice = -2;
                }
            }

            @Override
            public void afterTextChanged(Editable s) {
            }
        });

        /*
            CUT THRESHOLD
         */

        thresholdEdit.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {

            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                try {
                    cutthreshhold = Integer.valueOf(s.toString());
                } catch (NumberFormatException e) {
                    cutthreshhold = 0;
                }
            }

            @Override
            public void afterTextChanged(Editable s) {

            }
        });

        /*
            CONFIRM BUTTON
         */

        Button confirm = findViewById(R.id.confirm);
        confirm.setOnClickListener(v -> {
            try {
                JSONObject object = new JSONObject("{}");

                object.put("delay", delay);
                object.put("auxout", outputBool);
                if (outputDevice >= 0) {
                    object.put("outputdevice", outputDevice);
                } else {
                    if (outputDevice == -1) {
                        throw new JSONException("Missing Output Device");
                    } else {
                        if (outputDevice == -2) {
                            object.put("outputdevice", outputDevice);
                        } else {
                            throw new JSONException("Wrong Output Device" + outputDevice);
                        }
                    }
                }
                object.put("input_type", input_type);
                object.put("output_type", output_type);
                object.put("cutthreshold", cutthreshhold);
                if (inputDevice != -1) {
                    object.put("inputdevice", inputDevice);
                } else {
                    throw new JSONException("Wrong Input Device" + inputDevice);
                }

                object.put("lightson", lightsOn);
                object.put("chromecastname", chromecastname);

                new Thread(() -> {
                    String retu = setSettings(object, ip);
                    runOnUiThread(() -> new AlertDialog.Builder(context)
                            .setTitle("Web Request")
                            .setMessage(retu + object.toString())
                            .show());
                }).start();
            } catch (JSONException e) {
                new AlertDialog.Builder(context)
                        .setTitle("Error")
                        .setMessage("Configuration Error " + e)
                        .show();
            }
        });


    }
}
