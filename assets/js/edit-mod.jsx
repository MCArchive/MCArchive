import React, {Component} from 'react';
import {render} from 'react-dom';
import {Formik, Form, Field, FieldArray, ErrorMessage} from 'formik';
import * as yup from 'yup';

//import TagInput from './formik-tags.jsx';
import ReactTags from 'react-tag-autocomplete';

let DB_NAME_LEN = 80;
let DB_URL_LEN = 120;

// Transform null values to empty strings
yup.addMethod(yup.string, 'optional', function() {
    return this.transform(function(value, originalValue) {
        if (this.isType(value)) return value;
        else if (value === null) return '';
    });
});

let ModSchema = yup.object().shape({
    name: yup.string().max(DB_NAME_LEN).required(),
    desc: yup.string().optional(),
    website: yup.string().max(DB_URL_LEN).optional(),

    mod_vsns: yup.array().min(0).of(yup.object().shape({
        name: yup.string().max(DB_NAME_LEN).required(),
        desc: yup.string().optional(),
        url: yup.string().max(DB_URL_LEN).optional(),

        files: yup.array().min(1).of(yup.object().shape({
            desc: yup.string().optional(),
            page_url: yup.string().max(DB_URL_LEN).optional(),
            redirect_url: yup.string().max(DB_URL_LEN).optional(),
            direct_url: yup.string().max(DB_URL_LEN).optional(),
        })),
    })),
});

// mod_json is a global variable passed in through a jinja template
const initVals = ModSchema.validateSync(mod_json)

const ModForm = () => (
    <Formik
        initialValues={initVals}
        validationSchema={ModSchema}
        onSubmit={(values, { setSubmitting }) => {
            console.log(values);
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify(values),
            }).then(r => {
                if (r.ok) {
                    return r.json();
                } else {
                    throw Error(r.statusText);
                }
            }).then(data => {
                console.log(data);
                if (data.hasOwnProperty('result')) {
                    if (data['result'] == 'success') {
                        alert("Changes saved");
                        window.location.href = data['redirect'];
                    } else if (data.hasOwnProperty('result') && data['result'] == 'success') {
                        alert("Error submitting changes: " + data['error']);
                    } else {
                        alert("Received invalid response");
                    }
                } else {
                    alert("Received invalid response");
                }
            }).catch(error => {
                console.log(error);
                alert("Error submitting changes")
            }).finally(() => {
                setSubmitting(false);
            });
        }}
    >
        {({ isSubmitting }) => (
            <Form>
                <h2>Mod Info</h2>
                <table className="form-table">
                    <tbody>
                        <tr>
                            <td><label htmlFor="name">Name: </label></td>
                            <td><Field autoComplete='off' type="text" name="name" /></td>
                            <td><ErrorMessage name="name" component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor="website">Website: </label></td>
                            <td><Field autoComplete='off' type="text" name="website" /></td>
                            <td><ErrorMessage name="website" component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor="authors">Authors: </label></td>
                            <td><Field name="authors" component={TagInput}
                                    suggestions={authors_json} placeholder="Add an author"
                                /></td>
                            <td><ErrorMessage name="authors" component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor="desc">Description:</label></td>
                            <td><Field autoComplete='off' component="textarea" name="desc" /></td>
                            <td><ErrorMessage name="desc" component="div" /></td>
                        </tr>
                    </tbody>
                </table>

                <hr/>
                
                <h2>Mod Versions</h2>
                <FieldArray name="mod_vsns" component={VersionListForm}/>

                <hr/>

                <button type="submit" disabled={isSubmitting}>
                    Submit Changes
                </button>
            </Form>
        )}
    </Formik>
);

const blankFile = () => ({
    desc: '', page_url: '', redirect_url: '', direct_url: '',
});

const VersionListForm = ({
    move, swap, push, insert, unshift, pop, form, remove
}) => (
    <div className="edit-versions">
        {form.values.mod_vsns.map((vsn, index) => {
            var pfx = `mod_vsns.${index}`;

            return <div key={index} className="block edit-version">
                <button type="button" onClick={() => remove(index)}
                    style={{float: "right"}} tabIndex={-1}
                >Remove</button>
                <table className="form-table">
                    <tbody>
                        <tr>
                            <td><label htmlFor={pfx+".name"}>Name: </label></td>
                            <td><Field autoComplete='off' type="text" name={pfx+".name"}
                                       style={{"fontSize": "36px"}}
                                /></td>
                            <td><ErrorMessage name={pfx+".name"} component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor={pfx+".game_vsns"}>Game Versions: </label></td>
                            <td><Field name={pfx+".game_vsns"} component={TagInput}
                                    suggestions={game_vsns_json} placeholder="Add a version"
                                /></td>
                            <td><ErrorMessage name={pfx+".game_vsns"} component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor={pfx+".url"}>Web Page: </label></td>
                            <td><Field autoComplete='off' type="text" name={pfx+".url"} /></td>
                            <td><ErrorMessage name={pfx+".url"} component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor={pfx+".desc"}>Description:</label></td>
                            <td><Field autoComplete='off' component="textarea" name={pfx+".desc"} /></td>
                            <td><ErrorMessage name={pfx+".desc"} component="div" /></td>
                        </tr>
                    </tbody>
                </table>

                <h3>Files</h3>
                <FieldArray name={pfx+".files"} render={fprops => {
                    // We need to pass the version index into the file list form.
                    fprops['vsnidx'] = index;
                    return FileListForm(fprops);
                }}/>
            </div>
        })}
        <button type="button" onClick={() => push({
            name: '', desc: '', url: '', game_vsns: [], files: [blankFile()],
        })}>Add Version</button>
    </div>
);


const FileListForm = ({
    move, swap, push, insert, unshift, pop, form, remove, vsnidx
}) => {
    return <div className="edit-files">
        {form.values.mod_vsns[vsnidx].files.map((f, index) => {
            const pfx = `mod_vsns.${vsnidx}.files.${index}`;

            return <div key={index} className="sub-block edit-file">
                <button type="button" onClick={() => remove(index)}
                    style={{float: "right"}} tabIndex={-1}
                >Remove</button>
               <table className="form-table">
                    <tbody>
                        <tr>
                            <td><label htmlFor={pfx+".page_url"}>Web Page: </label></td>
                            <td><Field type="text" name={pfx+".page_url"} /></td>
                            <td><ErrorMessage name={pfx+".page_url"} component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor={pfx+".redirect_url"}>Redirect Download: </label></td>
                            <td><Field type="text" name={pfx+".redirect_url"} /></td>
                            <td><ErrorMessage name={pfx+".redirect_url"} component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor={pfx+".direct_url"}>Direct Download: </label></td>
                            <td><Field type="text" name={pfx+".direct_url"} /></td>
                            <td><ErrorMessage name={pfx+".direct_url"} component="div" /></td>
                        </tr>
                        <tr>
                            <td><label htmlFor={pfx+".desc"}>Description:</label></td>
                            <td><Field component="textarea" name={pfx+".desc"} /></td>
                            <td><ErrorMessage name={pfx+".desc"} component="div" /></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        })}
        <button type="button" onClick={() => push(blankFile())}>Add File</button>
    </div>
};

class TagInput extends Component {
    constructor(props) {
        super(props);
        this.state = {tags: props.field.value};
        this.classes = {
            root: 'tags',
            rootFocused: 'is-focused',
            selected: 'tags-selected',
            selectedTag: 'tag',
            selectedTagName: 'tag-name',
            search: 'tags-search',
            searchInput: 'tags-search-input',
            suggestions: 'tags-suggestions',
            suggestionActive: 'is-active',
            suggestionDisabled: 'is-disabled'
        }
    }

    handleAdd(tag) {
        const tags = [].concat(this.state.tags, tag);
        this.setState({tags});
        this.props.form.setFieldValue(this.props.field.name, tags);
    }

    handleDel(i) {
        const tags = this.state.tags.slice(0);
        tags.splice(i, 1);
        this.setState({tags});
        this.props.form.setFieldValue(this.props.field.name, tags);
    }

    render() {
        const field = this.props.field;
        return <div>
            <ReactTags tags={this.state.tags} name={field.name} onBlur={field.onBlur}
                handleAddition={this.handleAdd.bind(this)}
                handleDelete={this.handleDel.bind(this)}
                allowNew={true} classNames={this.classes}
                {...this.props}
            />
        </div>;
    }
};


render(<ModForm />, document.getElementById('mod-form'));

